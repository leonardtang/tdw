import numpy as np
import math
import base64
import json
import scipy.signal as sg
from enum import Enum
from typing import Dict, Optional, Tuple, Union, List
from tdw.output_data import OutputData, Rigidbodies, Collision, EnvironmentCollision
from pathlib import Path
from pkg_resources import resource_filename
from csv import DictReader
import io


class AudioMaterial(Enum):
    """
    These are the materials currently supported for impact sounds in pyImpact.  More will be added in time.
    """

    ceramic = 0
    glass = 1
    metal = 2
    hardwood = 3
    wood = 4
    cardboard = 5


class ObjectInfo:
    """
    Impact sound data for an object in a TDW model library.
    The audio values here are just recommendations; you can apply different values if you want.
    """

    def __init__(self, name: str, amp: float, mass: float, material: AudioMaterial, library: str, bounciness: float):
        """
        :param name: The model name.
        :param amp: The sound amplitude.
        :param mass: The object mass.
        :param material: The audio material.
        :param library: The path to the model library (see ModelLibrarian documentation).
        :param bounciness: The bounciness value for a Unity physics material.
        """

        self.amp = amp
        self.library = library
        self.mass = mass
        self.material = material
        self.name = name
        self.bounciness = bounciness


# Density per audio material.
DENSITIES: Dict[AudioMaterial, float] = {AudioMaterial.ceramic: 2180,
                                         AudioMaterial.glass: 2500,
                                         AudioMaterial.metal: 8450,
                                         AudioMaterial.hardwood: 900,
                                         AudioMaterial.wood: 690,
                                         AudioMaterial.cardboard: 698}


class Base64Sound:
    """
    A sound encoded as a base64 string.
    """

    def __init__(self, snd: np.array):
        """
        :param snd: The sound byte array.
        """

        tst1 = np.array(snd * 32767, dtype='int16')
        tst2 = bytes(tst1)
        tst3 = base64.b64encode(tst2).decode('utf-8')

        self.wav_str = tst3
        self.length = len(tst2)


class Modes:
    """
    Resonant mode properties: Frequencies, powers, and times.
    """

    def __init__(self, frequencies: np.array, powers: np.array, decay_times: np.array):
        """
        :param frequencies: numpy array of mode frequencies in Hz
        :param powers: numpy array of mode onset powers in dB re 1.
        :param decay_times: numpy array of mode decay times (i.e. the time in ms it takes for each mode to decay 60dB from its onset power)
        """
        self.frequencies = frequencies
        self.powers = powers
        self.decay_times = decay_times

    def sum_modes(self, fs: int = 44100) -> np.array:
        """
        Create mode time-series from mode properties and sum them together.

        :return A synthesized sound.
        """

        # Scroll through modes
        for i in range(len(self.frequencies)):
            H_dB = 80 + self.powers[i]
            L_ms = self.decay_times[i] * H_dB / 60
            mLen = math.ceil(L_ms / 1e3 * fs)
            # if mode length is greater than the current time-series we have had make our time series longer
            max_len = mLen
            if mLen > max_len:
                max_len = mLen
            tt = np.arange(0, max_len) / fs
            # synthesize a sinusoid
            mode = np.cos(2 * math.pi * self.frequencies[i] * tt)
            mode = mode * (10 ** (self.powers[i] / 20))
            dcy = tt * (60 / (self.decay_times[i] / 1e3))
            env = 10 ** (-dcy / 20)
            mode = mode * env
            if i == 0:
                synth_sound = mode
            else:
                synth_sound = Modes.mode_add(synth_sound, mode)
        return synth_sound

    @staticmethod
    def mode_add(a: np.array, b: np.array) -> np.array:
        """
        Add together numpy arrays of different lengths by zero-padding the shorter.

        :param a: The first array.
        :param b: The second array.

        :return The summed modes.
        """

        if len(a) < len(b):
            c = b.copy()
            c[:len(a)] += a
        else:
            c = a.copy()
            c[:len(b)] += b
        return c


class CollisionInfo:
    """
    Class containing information about collisions required by pyImpact to determine the volume of impact sounds.
    """

    def __init__(self, obj1_modes: Modes, obj2_modes: Modes, amp: float = 0.5, init_speed: float = 1):
        """
        :param amp: Amplitude of the first collision (must be between 0 and 1).
        :param init_speed: The speed of the initial collision (all collisions will be scaled relative to this).
        :param obj1_modes: The object's modes.
        :param obj2_modes: The other object's modes.
        """

        self.count = 0
        self.amp = amp
        # The speed of the initial collision.
        self.init_speed = init_speed
        # The audio modes.
        self.obj1_modes = obj1_modes
        self.obj2_modes = obj2_modes

    def count_collisions(self) -> None:
        """
        Update the counter for how many times two objects have collided.
        """

        self.count += 1


class PyImpact:
    """
    Generate impact sounds from physics data.

    Sounds are synthesized as described in: [Traer,Cusimano and McDermott, A PERCEPTUALLY INSPIRED GENERATIVE MODEL OF RIGID-BODY CONTACT SOUNDS, Digital Audio Effects, (DAFx), 2019](http://dafx2019.bcu.ac.uk/papers/DAFx2019_paper_57.pdf)

    For a general guide on impact sounds in TDW, read [this](../misc_frontend/impact_sounds.md).

    Usage:

    ```python
    from tdw.controller import Controller
    from tdw.py_impact import PyImpact

    p = PyImpact()
    c = Controller()
    c.start()

    # Your code here.

    c.communicate(p.get_impact_sound_command(arg1, arg2, ... ))
    ```
    """

    def __init__(self, initial_amp: float = 0.5, prevent_distortion: bool = True):
        """
        :param initial_amp: The initial amplitude, i.e. the "master volume". Must be > 0 and < 1.
        :param prevent_distortion: If True, clamp amp values to <= 0.99
        """

        assert 0 < initial_amp < 1, f"initial_amp is {initial_amp} (must be > 0 and < 1)."

        self.initial_amp = initial_amp
        self.prevent_distortion = prevent_distortion

        # The collision info per set of objects.
        self.object_modes: Dict[int, Dict[int, CollisionInfo]] = {}

        # Cache the material data. This is use to reset the material modes.
        self.material_data: Dict[str, dict] = {}
        for mat, path in zip(["ceramic", "hardwood", "metal", "glass", "wood", "cardboard"],
                             ["Ceramic_mm", "Poplar_mm", "MetalStrip_mm", "Mirror_mm", "BalsaWood_mm", "Cardboard_mm"]):
            # Load the JSON data.
            data = json.loads(Path(resource_filename(__name__, f"py_impact/material_data/{path}.json")).read_text())
            self.material_data.update({mat: data})

    def _get_object_modes(self, material: Union[str, AudioMaterial]) -> Modes:
        """
        :param material: The audio material.

        :return: The audio modes.
        """

        data = self.material_data[material] if isinstance(material, str) else self.material_data[material.name]
        # Load the mode properties.
        f = -1
        p = -1
        t = -1
        for jm in range(0, 10):
            jf = 0
            while jf < 20:
                jf = data["cf"][jm] + np.random.normal(0, data["cf"][jm] / 10)
            jp = data["op"][jm] + np.random.normal(0, 10)
            jt = 0
            while jt < 0.001:
                jt = data["rt"][jm] + np.random.normal(0, data["rt"][jm] / 10)
            if jm == 0:
                f = jf
                p = jp
                t = jt * 1e3
            else:
                f = np.append(f, jf)
                p = np.append(p, jp)
                t = np.append(t, jt * 1e3)
        return Modes(f, p, t)

    def get_sound(self, collision: Union[Collision, EnvironmentCollision], rigidbodies: Rigidbodies, id1: int, mat1: str, id2: int, mat2: str, amp2re1: float) -> Optional[Base64Sound]:
        """
        Produce sound of two colliding objects as a byte array.

        :param collision: TDW `Collision` or `EnvironmentCollision` output data.
        :param rigidbodies: TDW `Rigidbodies` output data.
        :param id1: The object ID for one of the colliding objects.
        :param mat1: The material label for one of the colliding objects.
        :param id2: The object ID for the other object.
        :param mat2: The material label for the other object.
        :param amp2re1: The sound amplitude of object 2 relative to that of object 1.

        :return Sound data as a Base64Sound object.
        """

        # Set the object modes.
        if id2 not in self.object_modes:
            self.object_modes.update({id2: {}})
        if id1 not in self.object_modes[id2]:
            self.object_modes[id2].update({id1: CollisionInfo(self._get_object_modes(mat2),
                                                              self._get_object_modes(mat1),
                                                              amp=self.initial_amp)})

        obj_col = isinstance(collision, Collision)

        # Unpack useful parameters.
        # Compute normal velocity at impact.
        vel = 0
        if obj_col:
            vel = collision.get_relative_velocity()
        else:
            for i in range(rigidbodies.get_num()):
                if rigidbodies.get_id(i) == id2:
                    vel = rigidbodies.get_velocity(i)
                    break
        vel = np.asarray(vel)
        speed = np.square(vel)
        speed = np.sum(speed)
        speed = math.sqrt(speed)
        nvel = vel / np.linalg.norm(vel)
        num_contacts = collision.get_num_contacts()
        nspd = []
        for jc in range(0, num_contacts):
            tmp = np.asarray(collision.get_contact_normal(jc))
            tmp = tmp / np.linalg.norm(tmp)
            tmp = np.arccos(np.clip(np.dot(tmp, nvel), -1.0, 1.0))
            # Scale the speed by the angle (i.e. we want speed Normal to the surface).
            tmp = speed * np.cos(tmp)
            nspd.append(tmp)
        normal_speed = np.mean(nspd)
        # Get indices of objects in collisions
        id1_index = None
        id2_index = None
        for i in range(rigidbodies.get_num()):
            if rigidbodies.get_id(i) == id1:
                id1_index = i
            if rigidbodies.get_id(i) == id2:
                id2_index = i

        # Make sure both IDs were found. If they aren't, don't return a sound.
        if obj_col and (id1_index is None or id2_index is None):
            return None

        m1 = rigidbodies.get_mass(id1_index) if obj_col else 1000
        m2 = rigidbodies.get_mass(id2_index)
        mass = np.min([m1, m2])

        # Re-scale the amplitude.
        if self.object_modes[id2][id1].count == 0:
            # Sample the modes.
            sound, modes_1, modes_2 = self.make_impact_audio(amp2re1, mass, mat1=mat1, mat2=mat2, id1=id1, id2=id2)
            # Save collision info - we will need for later collisions.
            amp = self.object_modes[id2][id1].amp
            self.object_modes[id2][id1].init_speed = normal_speed
            self.object_modes[id2][id1].obj1_modes = modes_1
            self.object_modes[id2][id1].obj2_modes = modes_2
        else:
            amp = self.object_modes[id2][id1].amp * normal_speed / self.object_modes[id2][id1].init_speed
            # Adjust modes here so that two successive impacts are not identical.
            modes_1 = self.object_modes[id2][id1].obj1_modes
            modes_2 = self.object_modes[id2][id1].obj2_modes
            modes_1.powers = modes_1.powers + np.random.normal(0, 2, len(modes_1.powers))
            modes_2.power = modes_2.powers + np.random.normal(0, 2, len(modes_1.powers))
            sound = PyImpact.synth_impact_modes(modes_1, modes_2, mass)
            self.object_modes[id2][id1].obj1_modes = modes_1
            self.object_modes[id2][id1].obj2_modes = modes_2

        # On rare occasions, it is possible for PyImpact to fail to generate a sound.
        if sound is None:
            return None

        # Count the collisions.
        self.object_modes[id2][id1].count_collisions()

        # Prevent distortion by clamping the amp.
        if self.prevent_distortion and amp > 0.99:
            amp = 0.99

        sound = amp * sound / np.max(np.abs(sound))
        return Base64Sound(sound)

    def get_impact_sound_command(self, collision: Union[Collision, EnvironmentCollision], rigidbodies: Rigidbodies, target_id: int, target_mat: str, target_amp: float, other_id: int, other_mat: str, other_amp: float, play_audio_data: bool = True) -> dict:
        """
        Create an impact sound, and return a valid command to play audio data in TDW.
        "target" should usually be the smaller object, which will play the sound.
        "other" should be the larger (stationary) object.

        :param collision: TDW `Collision` or `EnvironmentCollision` output data.
        :param target_amp: The target's amp value.
        :param target_mat: The target's audio material.
        :param other_amp: The other object's amp value.
        :param other_id: The other object's ID.
        :param other_mat: The other object's audio material.
        :param rigidbodies: TDW `Rigidbodies` output data.
        :param target_id: The ID of the object that will play the sound.
        :param play_audio_data: If True, return a `play_audio_data` command. If False, return a `play_point_source_data` command (useful only with Resonance Audio; see Command API).

        :return A `play_audio_data` or `play_point_source_data` command that can be sent to the build via `Controller.communicate()`.
        """

        amp2re1 = other_amp / target_amp

        impact_audio = self.get_sound(collision, rigidbodies, other_id, other_mat, target_id, target_mat, amp2re1)
        if impact_audio is not None:
            return {"$type": "play_audio_data" if play_audio_data else "play_point_source_data",
                    "id": target_id,
                    "num_frames": impact_audio.length,
                    "num_channels": 1,
                    "frame_rate": 44100,
                    "wav_data": impact_audio.wav_str,
                    "y_pos_offset": 0.1}
        # If PyImpact failed to generate a sound (which is rare!), fail silently here.
        else:
            return {"$type": "do_nothing"}

    def make_impact_audio(self, amp2re1: float, mass: float, id1: int, id2: int, mat1: str = 'cardboard', mat2: str = 'cardboard') -> (np.array, Modes, Modes):
        """
        Generate an impact sound.

        :param mat1: The material label for one of the colliding objects.
        :param mat2: The material label for the other object.
        :param amp2re1: The sound amplitude of object 2 relative to that of object 1.
        :param mass: The mass of the smaller of the two colliding objects.
        :param id1: The ID for the one of the colliding objects.
        :param id2: The ID for the other object.

        :return The sound, and the object modes.
        """

        # Unpack material names.
        for jmat in range(0, len(AudioMaterial)):
            if mat1 == AudioMaterial(jmat):
                tmp1 = AudioMaterial(jmat)
                mat1 = tmp1.name
            if mat2 == AudioMaterial(jmat):
                tmp2 = AudioMaterial(jmat)
                mat2 = tmp2.name
        # Sample modes of object1.
        modes_1 = self.object_modes[id2][id1].obj1_modes
        modes_2 = self.object_modes[id2][id1].obj2_modes
        # Scale the two sounds as specified.
        modes_2.decay_times = modes_2.decay_times + 20 * np.log10(amp2re1)
        snth = PyImpact.synth_impact_modes(modes_1, modes_2, mass)
        return snth, modes_1, modes_2

    @staticmethod
    def synth_impact_modes(modes1: Modes, modes2: Modes, mass: float) -> np.array:
        """
        Generate an impact sound from specified modes for two objects, and the mass of the smaller object.

        :param modes1: Modes of object 1. A numpy array with: column1=mode frequencies (Hz); column2=mode onset powers in dB; column3=mode RT60s in milliseconds;
        :param modes2: Modes of object 2. Formatted as modes1/modes2.
        :param mass: the mass of the smaller of the two colliding objects.

        :return The impact sound.
        """

        h1 = modes1.sum_modes()
        h2 = modes2.sum_modes()
        h = Modes.mode_add(h1, h2)
        if len(h) == 0:
            return None
        # Convolve with force, with contact time scaled by the object mass.
        max_t = 0.001 * mass
        # A contact time over 2ms is unphysically long.
        max_t = np.min([max_t, 2e-3])
        n_pts = int(np.ceil(max_t * 44100))
        tt = np.linspace(0, np.pi, n_pts)
        frc = np.sin(tt)
        x = sg.fftconvolve(h, frc)
        x = x / abs(np.max(x))
        return x

    @staticmethod
    def get_object_info(csv_file: Union[str, Path] = "") -> Dict[str, ObjectInfo]:
        """
        Returns ObjectInfo values.
        As of right now, only a few objects in the TDW model libraries are included. More will be added in time.

        :param csv_file: The path to the .csv file containing the object info. By default, it will load `tdw/py_impact/objects.csv`. If you want to make your own spreadsheet, use this file as a reference.

        :return: A list of default ObjectInfo. Key = the name of the model. Value = object info.
        """

        objects: Dict[str, ObjectInfo] = {}
        # Load the objects.csv metadata file.
        if isinstance(csv_file, str):
            # Load the default file.
            if csv_file == "":
                csv_file = str(Path(resource_filename(__name__, f"py_impact/objects.csv")).resolve())
            else:
                csv_file = str(Path(csv_file).resolve())
        else:
            csv_file = str(csv_file.resolve())

        # Parse the .csv file.
        with io.open(csv_file, newline='', encoding='utf-8-sig') as f:
            reader = DictReader(f)
            for row in reader:
                o = ObjectInfo(name=row["name"], amp=float(row["amp"]), mass=float(row["mass"]),
                               material=AudioMaterial[row["material"]], library=row["library"],
                               bounciness=float(row["bounciness"]))
                objects.update({o.name: o})

        return objects

    @staticmethod
    def get_collisions(resp: List[bytes]) -> Tuple[List[Collision], List[EnvironmentCollision], Optional[Rigidbodies]]:
        """
        Parse collision and rigibody data from the output data.

        :param resp: The response from the build.

        :return: A list of collisions on this frame (can be empty), a list of environment collisions on this frame (can be empty), and Rigidbodies data (can be `None`).
        """

        if len(resp) == 1:
            return [], [], None
        collisions: List[Collision] = []
        environment_collisions: List[EnvironmentCollision] = []
        rigidbodies: Optional[Rigidbodies] = None
        for r in resp[:-1]:
            r_id = OutputData.get_data_type_id(r)
            if r_id == 'coll':
                collisions.append(Collision(r))
            if r_id == 'rigi':
                rigidbodies = Rigidbodies(r)
            if r_id == 'enco':
                environment_collisions.append(EnvironmentCollision(r))

        return collisions, environment_collisions, rigidbodies

    @staticmethod
    def is_valid_collision(collision: Union[Optional[Collision], Optional[EnvironmentCollision]]) -> bool:
        """
        :param collision: Collision or EnvironmentCollision output data from the build.

        :return: True if this collision can be used to generate an impact sound.
        """

        return collision is not None and ((isinstance(collision, Collision) and
                                           np.linalg.norm(collision.get_relative_velocity()) > 0) or
                                          isinstance(collision, EnvironmentCollision))

    def reset(self, initial_amp: float = 0.5) -> None:
        """
        Reset PyImpact. This is somewhat faster than creating a new PyImpact object per trial.

        :param initial_amp: The initial amplitude, i.e. the "master volume". Must be > 0 and < 1.
        """

        assert 0 < initial_amp < 1, f"initial_amp is {initial_amp} (must be > 0 and < 1)."

        # Clear the object data.
        self.object_modes.clear()

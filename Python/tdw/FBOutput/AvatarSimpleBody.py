# automatically generated by the FlatBuffers compiler, do not modify

# namespace: FBOutput

import tdw.flatbuffers

class AvatarSimpleBody(object):
    __slots__ = ['_tab']

    @classmethod
    def GetRootAsAvatarSimpleBody(cls, buf, offset):
        n = tdw.flatbuffers.encode.Get(tdw.flatbuffers.packer.uoffset, buf, offset)
        x = AvatarSimpleBody()
        x.Init(buf, n + offset)
        return x

    # AvatarSimpleBody
    def Init(self, buf, pos):
        self._tab = tdw.flatbuffers.table.Table(buf, pos)

    # AvatarSimpleBody
    def Id(self):
        o = tdw.flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(4))
        if o != 0:
            return self._tab.String(o + self._tab.Pos)
        return None

    # AvatarSimpleBody
    def Position(self):
        o = tdw.flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(6))
        if o != 0:
            x = o + self._tab.Pos
            from .Vector3 import Vector3
            obj = Vector3()
            obj.Init(self._tab.Bytes, x)
            return obj
        return None

    # AvatarSimpleBody
    def Rotation(self):
        o = tdw.flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(8))
        if o != 0:
            x = o + self._tab.Pos
            from .Quaternion import Quaternion
            obj = Quaternion()
            obj.Init(self._tab.Bytes, x)
            return obj
        return None

    # AvatarSimpleBody
    def Forward(self):
        o = tdw.flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(10))
        if o != 0:
            x = o + self._tab.Pos
            from .Vector3 import Vector3
            obj = Vector3()
            obj.Init(self._tab.Bytes, x)
            return obj
        return None

    # AvatarSimpleBody
    def Velocity(self):
        o = tdw.flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(12))
        if o != 0:
            x = o + self._tab.Pos
            from .Vector3 import Vector3
            obj = Vector3()
            obj.Init(self._tab.Bytes, x)
            return obj
        return None

    # AvatarSimpleBody
    def AngularVelocity(self):
        o = tdw.flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(14))
        if o != 0:
            x = o + self._tab.Pos
            from .Vector3 import Vector3
            obj = Vector3()
            obj.Init(self._tab.Bytes, x)
            return obj
        return None

    # AvatarSimpleBody
    def Mass(self):
        o = tdw.flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(16))
        if o != 0:
            return self._tab.Get(tdw.flatbuffers.number_types.Float32Flags, o + self._tab.Pos)
        return 0.0

    # AvatarSimpleBody
    def Sleeping(self):
        o = tdw.flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(18))
        if o != 0:
            return bool(self._tab.Get(tdw.flatbuffers.number_types.BoolFlags, o + self._tab.Pos))
        return False

    # AvatarSimpleBody
    def VisibleBody(self):
        o = tdw.flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(20))
        if o != 0:
            return self._tab.String(o + self._tab.Pos)
        return None

def AvatarSimpleBodyStart(builder): builder.StartObject(9)
def AvatarSimpleBodyAddId(builder, id): builder.PrependUOffsetTRelativeSlot(0, tdw.flatbuffers.number_types.UOffsetTFlags.py_type(id), 0)
def AvatarSimpleBodyAddPosition(builder, position): builder.PrependStructSlot(1, tdw.flatbuffers.number_types.UOffsetTFlags.py_type(position), 0)
def AvatarSimpleBodyAddRotation(builder, rotation): builder.PrependStructSlot(2, tdw.flatbuffers.number_types.UOffsetTFlags.py_type(rotation), 0)
def AvatarSimpleBodyAddForward(builder, forward): builder.PrependStructSlot(3, tdw.flatbuffers.number_types.UOffsetTFlags.py_type(forward), 0)
def AvatarSimpleBodyAddVelocity(builder, velocity): builder.PrependStructSlot(4, tdw.flatbuffers.number_types.UOffsetTFlags.py_type(velocity), 0)
def AvatarSimpleBodyAddAngularVelocity(builder, angularVelocity): builder.PrependStructSlot(5, tdw.flatbuffers.number_types.UOffsetTFlags.py_type(angularVelocity), 0)
def AvatarSimpleBodyAddMass(builder, mass): builder.PrependFloat32Slot(6, mass, 0.0)
def AvatarSimpleBodyAddSleeping(builder, sleeping): builder.PrependBoolSlot(7, sleeping, 0)
def AvatarSimpleBodyAddVisibleBody(builder, visibleBody): builder.PrependUOffsetTRelativeSlot(8, tdw.flatbuffers.number_types.UOffsetTFlags.py_type(visibleBody), 0)
def AvatarSimpleBodyEnd(builder): return builder.EndObject()
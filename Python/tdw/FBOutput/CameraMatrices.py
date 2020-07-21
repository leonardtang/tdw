# automatically generated by the FlatBuffers compiler, do not modify

# namespace: FBOutput

import tdw.flatbuffers

class CameraMatrices(object):
    __slots__ = ['_tab']

    @classmethod
    def GetRootAsCameraMatrices(cls, buf, offset):
        n = tdw.flatbuffers.encode.Get(tdw.flatbuffers.packer.uoffset, buf, offset)
        x = CameraMatrices()
        x.Init(buf, n + offset)
        return x

    # CameraMatrices
    def Init(self, buf, pos):
        self._tab = tdw.flatbuffers.table.Table(buf, pos)

    # CameraMatrices
    def AvatarId(self):
        o = tdw.flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(4))
        if o != 0:
            return self._tab.String(o + self._tab.Pos)
        return None

    # CameraMatrices
    def SensorName(self):
        o = tdw.flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(6))
        if o != 0:
            return self._tab.String(o + self._tab.Pos)
        return None

    # CameraMatrices
    def ProjectionMatrix(self, j):
        o = tdw.flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(8))
        if o != 0:
            a = self._tab.Vector(o)
            return self._tab.Get(tdw.flatbuffers.number_types.Float32Flags, a + tdw.flatbuffers.number_types.UOffsetTFlags.py_type(j * 4))
        return 0

    # CameraMatrices
    def ProjectionMatrixAsNumpy(self):
        o = tdw.flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(8))
        if o != 0:
            return self._tab.GetVectorAsNumpy(tdw.flatbuffers.number_types.Float32Flags, o)
        return 0

    # CameraMatrices
    def ProjectionMatrixLength(self):
        o = tdw.flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(8))
        if o != 0:
            return self._tab.VectorLen(o)
        return 0

    # CameraMatrices
    def CameraMatrix(self, j):
        o = tdw.flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(10))
        if o != 0:
            a = self._tab.Vector(o)
            return self._tab.Get(tdw.flatbuffers.number_types.Float32Flags, a + tdw.flatbuffers.number_types.UOffsetTFlags.py_type(j * 4))
        return 0

    # CameraMatrices
    def CameraMatrixAsNumpy(self):
        o = tdw.flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(10))
        if o != 0:
            return self._tab.GetVectorAsNumpy(tdw.flatbuffers.number_types.Float32Flags, o)
        return 0

    # CameraMatrices
    def CameraMatrixLength(self):
        o = tdw.flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(10))
        if o != 0:
            return self._tab.VectorLen(o)
        return 0

def CameraMatricesStart(builder): builder.StartObject(4)
def CameraMatricesAddAvatarId(builder, avatarId): builder.PrependUOffsetTRelativeSlot(0, tdw.flatbuffers.number_types.UOffsetTFlags.py_type(avatarId), 0)
def CameraMatricesAddSensorName(builder, sensorName): builder.PrependUOffsetTRelativeSlot(1, tdw.flatbuffers.number_types.UOffsetTFlags.py_type(sensorName), 0)
def CameraMatricesAddProjectionMatrix(builder, projectionMatrix): builder.PrependUOffsetTRelativeSlot(2, tdw.flatbuffers.number_types.UOffsetTFlags.py_type(projectionMatrix), 0)
def CameraMatricesStartProjectionMatrixVector(builder, numElems): return builder.StartVector(4, numElems, 4)
def CameraMatricesAddCameraMatrix(builder, cameraMatrix): builder.PrependUOffsetTRelativeSlot(3, tdw.flatbuffers.number_types.UOffsetTFlags.py_type(cameraMatrix), 0)
def CameraMatricesStartCameraMatrixVector(builder, numElems): return builder.StartVector(4, numElems, 4)
def CameraMatricesEnd(builder): return builder.EndObject()
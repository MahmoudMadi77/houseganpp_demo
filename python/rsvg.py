import ctypes


class RsvgDimensionData(ctypes.Structure):
    _fields_ = [("width", ctypes.c_int),
                ("height", ctypes.c_int),
                ("em",ctypes.c_double),
                ("ex",ctypes.c_double)]


class PycairoContext(ctypes.Structure):
    _fields_ = [("PyObject_HEAD", ctypes.c_byte * object.__basicsize__),
                ("ctx", ctypes.c_void_p),
                ("base", ctypes.c_void_p)]


librsvg = ctypes.CDLL(r'C:\msys64\mingw64\bin\librsvg-2-2.dll')
libgobject = ctypes.CDLL(r'C:\msys64\mingw64\bin\libgobject-2.0-0.dll')


librsvg.rsvg_handle_new_from_data.argtypes = (ctypes.POINTER(ctypes.c_ubyte), ctypes.c_ulong, ctypes.POINTER(ctypes.c_void_p))
librsvg.rsvg_handle_new_from_data.restype = ctypes.c_void_p

librsvg.rsvg_handle_get_dimensions.argtypes = (ctypes.c_void_p, ctypes.POINTER(RsvgDimensionData))
librsvg.rsvg_handle_get_dimensions.restype = None

librsvg.rsvg_handle_render_cairo.argtypes = (ctypes.c_void_p, ctypes.c_void_p)
librsvg.rsvg_handle_render_cairo.restype = ctypes.c_int


libgobject.g_type_init.argtypes = tuple()
libgobject.g_type_init.restype = None


libgobject.g_type_init()


class Handle:
    def __init__(self, data):
        data = bytearray(data.encode())
        dataSize = len(data)
        ubuffer = (ctypes.c_ubyte * dataSize).from_buffer(data)
        self.handle = librsvg.rsvg_handle_new_from_data(ubuffer, dataSize, None)
        assert self.handle


    def get_dimension_data(self):
        svgDim = RsvgDimensionData()
        librsvg.rsvg_handle_get_dimensions(self.handle, ctypes.byref(svgDim))
        return (svgDim.width,svgDim.height)

    def render_cairo(self, ctx):
        ctx.save()
        z = PycairoContext.from_address(id(ctx))
        librsvg.rsvg_handle_render_cairo(self.handle, z.ctx)
        ctx.restore()

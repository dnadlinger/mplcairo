from matplotlib.backends.backend_wx import (
    _BackendWx, _FigureCanvasWxBase, FigureFrameWx, NavigationToolbar2Wx)
import wx

from . import base
from .base import FigureCanvasCairo


class FigureFrameWxCairo(FigureFrameWx):
    def get_canvas(self, fig):
        return FigureCanvasWxCairo(self, -1, fig)


# See Bitmap.FromBufferRGBA: "On Windows and Mac the RGB values will be
# 'premultiplied' by the alpha values. (The other platforms do the
# multiplication themselves.)
_to_native_bitmap = (
    base._to_premultiplied_rgba8888
    if wx.GetOsVersion()[0] & (wx.OS_WINDOWS | wx.OS_MAC) else
    base._to_unmultiplied_rgba8888)


class FigureCanvasWxCairo(FigureCanvasCairo, _FigureCanvasWxBase):
    def __init__(self, parent, id, figure):
        # _FigureCanvasWxBase should be fixed to have the same signature as
        # every other FigureCanvas and use cooperative inheritance, but in the
        # meantime we'll just inline the call to FigureCanvasCairo.__init__.
        self._last_renderer_call = None, None
        _FigureCanvasWxBase.__init__(self, parent, id, figure)

    def draw(self, drawDC=None):
        renderer = self.get_renderer(_draw_if_new=True)
        buf = renderer._get_buffer()
        height, width, _ = buf.shape
        self.bitmap = wx.Bitmap.FromBufferRGBA(
            width, height, base._to_unmultiplied_rgba8888(buf))
        self._isDrawn = True
        self.gui_repaint(drawDC=drawDC, origin='WXCairo')

    def blit(self, bbox=None):
        self.draw()


@_BackendWx.export
class _BackendWxCairo(_BackendWx):
    FigureCanvas = FigureCanvasWxCairo
    _frame_class = FigureFrameWxCairo

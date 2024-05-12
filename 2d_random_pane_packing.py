from OCC.Core.gp import gp_Pnt
from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeBox
from OCC.Core.BRepAlgoAPI import BRepAlgoAPI_Cut
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_Transform
from OCC.Core.Quantity import (
    Quantity_Color,
    Quantity_NameOfColor,
    Quantity_NOC_ALICEBLUE,
    Quantity_NOC_LIGHTBLUE,
)
from OCC.Core.TopExp import TopExp_Explorer
from OCC.Core.TopAbs import TopAbs_FACE, TopAbs_EDGE
from OCC.Core.TopoDS import topods_Face, topods_Edge
from OCC.Display.SimpleGui import init_display
import random

from OCC.Core.Bnd import Bnd_Box
from OCC.Core.BRepBndLib import brepbndlib_Add


class PackingApp:
    def __init__(self):
        self.display, self.start_display, _, _ = init_display()

        main_panel_width = 100
        main_panel_height = 300
        self.main_panel = BRepPrimAPI_MakeBox(main_panel_width, main_panel_height, 2).Shape()
        self.display.DisplayShape(self.main_panel, update=True, color="blue")

        self.smaller_panels = []
        self.fit_smaller_panels()

    def fit_smaller_panels(self):
        max_attempts = 40
        attempt = 0
        colors = [color for color in dir(Quantity_NameOfColor) if color.startswith("Quantity_NOC")]
        while attempt < max_attempts:
            width = random.uniform(10, 30)
            height = random.uniform(10, 30)
            start_point = gp_Pnt(random.uniform(0, 70), random.uniform(0, 270), 0)
            color = random.choice(colors)
            color = getattr(Quantity_NameOfColor, color)
            smaller_panel = BRepPrimAPI_MakeBox(start_point, gp_Pnt(start_point.X() + width, start_point.Y() + height, start_point.Z() + 10)).Shape()
            if not self.panel_overlaps(smaller_panel):
                self.smaller_panels.append(smaller_panel)
                self.display.DisplayShape(smaller_panel, update=True, color=color)
                attempt += 1
            #else:
            #    self.display.DisplayShape(smaller_panel, update=True, color="red")
            #    print("Pezzo non allocato: pannello troppo piccolo")

    def panel_overlaps(self, panel):
        panel_bbox = self.calculate_bounding_box(panel)
        for existing_panel in self.smaller_panels:
            existing_panel_bbox = self.calculate_bounding_box(existing_panel)
            if self.bounding_boxes_intersect(panel_bbox, existing_panel_bbox):
                return True
        return False

    def calculate_bounding_box(self, shape):
        bbox = Bnd_Box()
        brepbndlib_Add(shape, bbox)
        return bbox

    def bounding_boxes_intersect(self, bbox1, bbox2):
        return bbox1.IsOut(bbox2) == 0 or bbox2.IsOut(bbox1) == 0


if __name__ == "__main__":
    app = PackingApp()
    app.display.FitAll()
    app.start_display()
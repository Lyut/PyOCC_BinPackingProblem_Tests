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

        self.main_panel_width = 100
        self.main_panel_height = 300
        self.main_panel = BRepPrimAPI_MakeBox(self.main_panel_width, self.main_panel_height, 2).Shape()
        self.display.DisplayShape(self.main_panel, update=True, color="blue")

        self.smaller_panels = []
        self.panel_dimensions = [(80, 20), (55, 25), (99, 240)]
        self.fit_smaller_panels()

    def fit_smaller_panels(self):
        colors = [color for color in dir(Quantity_NameOfColor) if color.startswith("Quantity_NOC")]
        for width, height in self.panel_dimensions:
            start_point = self.find_empty_position(width, height)
            if start_point:
                color = random.choice(colors)
                color = getattr(Quantity_NameOfColor, color)
                smaller_panel = BRepPrimAPI_MakeBox(start_point, gp_Pnt(start_point.X() + width, start_point.Y() + height, start_point.Z() + 10)).Shape()
                if not self.panel_overlaps(smaller_panel):
                    self.smaller_panels.append(smaller_panel)
                    self.display.DisplayShape(smaller_panel, update=True, color=color)
            else:
                print(f"Pezzo non allocato: pannello troppo piccolo per accomodare pannello di lunghezza {height} e larghezza {width}")

    def find_empty_position(self, width, height):
        step = 1  # Step
        for x in range(0, self.main_panel_width - width, step):
            for y in range(0, self.main_panel_height - height, step):
                start_point = gp_Pnt(x, y, 0)
                if not self.panel_overlaps(BRepPrimAPI_MakeBox(start_point, gp_Pnt(start_point.X() + width, start_point.Y() + height, start_point.Z() + 10)).Shape()):
                    return start_point
                # Proviamo a ruotarlo
                if not self.panel_overlaps(BRepPrimAPI_MakeBox(start_point, gp_Pnt(start_point.X() + height, start_point.Y() + width, start_point.Z() + 10)).Shape()):
                    return start_point

        return None

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
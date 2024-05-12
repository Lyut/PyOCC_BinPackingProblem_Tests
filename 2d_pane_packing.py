import random
from OCC.Core.gp import gp_Ax1, gp_Pnt, gp_Dir, gp_Trsf, gp_Vec
from OCC.Core.BRepBuilderAPI import (
    BRepBuilderAPI_MakeEdge,
    BRepBuilderAPI_MakeWire,
    BRepBuilderAPI_MakeFace,
    BRepBuilderAPI_Transform,
    BRepBuilderAPI_MakeSolid
)
from OCC.Core.Quantity import (
    Quantity_Color,
    Quantity_NameOfColor,
    Quantity_NOC_ALICEBLUE,
    Quantity_NOC_LIGHTBLUE,
)
#from OCC.Core.BRepAlgoAPI import BRepAlgoAPI_Cut
from OCC.Core.TopExp import TopExp_Explorer
from OCC.Core.TopAbs import TopAbs_FACE, TopAbs_WIRE, TopAbs_EDGE, TopAbs_VERTEX
from OCC.Core.TopoDS import topods_Face, topods_Wire, topods_Edge, topods_Vertex
#from OCC.Core.BRep import BRep_Tool
from OCC.Display.SimpleGui import init_display
#from OCC.Core.GProp import GProp_GProps
#from OCC.Core.BRepGProp import brepgprop_VolumeProperties, brepgprop_SurfaceProperties
#from OCC.Core.BRep import BRep_Builder, BRep_Tool
#from OCC.Core.BRepTools import breptools
from OCC.Core.Bnd import Bnd_Box
from OCC.Core.BRepBndLib import brepbndlib_Add
#from OCC.Core.TopoDS import TopoDS_Shape


class PackingApp:
    def __init__(self):
        self.display, self.start_display, self.add_menu, self.add_function_to_menu = init_display()
        self.main_panel_width = 100
        self.main_panel_height = 300
        self.main_panel = self.create_plywood_panel(self.main_panel_width, self.main_panel_height, gp_Pnt(0, 0, 0))
        self.display.View.SetBgGradientColors(
            Quantity_Color(Quantity_NOC_ALICEBLUE),
            Quantity_Color(Quantity_NOC_LIGHTBLUE),
            2,
            True,
        )
        self.display.Repaint()
        self.display.DisplayShape(self.main_panel, update=True, color="blue")

        self.smaller_panels = []
        self.fit_smaller_panels()

    def fit_smaller_panels(self):
        max_attempts = 10
        attempt = 0
        colors = [color for color in dir(Quantity_NameOfColor) if color.startswith("Quantity_NOC")]
        while attempt < max_attempts:
            width = random.uniform(1, self.main_panel_width)
            height = random.uniform(1, self.main_panel_height)
            color = random.choice(colors)
            color = getattr(Quantity_NameOfColor, color)
            start_point = gp_Pnt(random.uniform(0, self.main_panel_width - width), random.uniform(0, self.main_panel_height - height), 0)
            smaller_panel = self.create_plywood_panel(width, height, start_point)
            if not self.panel_overlaps(smaller_panel):
                self.smaller_panels.append(smaller_panel)
                self.display.DisplayShape(smaller_panel, update=True, color=color)
                attempt += 1

    def panel_overlaps(self, panel):
        for existing_panel in self.smaller_panels:
            if self.panels_intersect(panel, existing_panel):
                return True
        return False

    def panels_intersect(self, panel1, panel2):
        def edge_intersection(edge1, edge2):
            bbox1 = Bnd_Box()
            bbox2 = Bnd_Box()
            brepbndlib_Add(edge1, bbox1)
            brepbndlib_Add(edge2, bbox2)
            return bbox1.IsOut(bbox2) == 0 or bbox2.IsOut(bbox1) == 0

        explorer = TopExp_Explorer(panel1, TopAbs_EDGE)
        edges1 = [topods_Edge(explorer.Current()) for _ in range(4)]
        explorer = TopExp_Explorer(panel2, TopAbs_EDGE)
        edges2 = [topods_Edge(explorer.Current()) for _ in range(4)]

        for edge1 in edges1:
            for edge2 in edges2:
                if edge_intersection(edge1, edge2):
                    return True
        return False

    def create_plywood_panel(self, width, height, start_point):
        p1 = start_point
        p2 = gp_Pnt(start_point.X() + width, start_point.Y(), start_point.Z())
        p3 = gp_Pnt(start_point.X() + width, start_point.Y() + height, start_point.Z())
        p4 = gp_Pnt(start_point.X(), start_point.Y() + height, start_point.Z())

        wire_builder = BRepBuilderAPI_MakeWire()
        wire_builder.Add(BRepBuilderAPI_MakeEdge(p1, p2).Edge())
        wire_builder.Add(BRepBuilderAPI_MakeEdge(p2, p3).Edge())
        wire_builder.Add(BRepBuilderAPI_MakeEdge(p3, p4).Edge())
        wire_builder.Add(BRepBuilderAPI_MakeEdge(p4, p1).Edge())

        face_builder = BRepBuilderAPI_MakeFace(wire_builder.Wire(), True)
        return face_builder.Face()

if __name__ == "__main__":
    app = PackingApp()
    app.display.FitAll()
    app.start_display()
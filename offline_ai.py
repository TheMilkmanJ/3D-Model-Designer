import re
import numpy as np
import trimesh
from PyQt6 import QtGui, QtCore, QtWidgets

def process_basic_command(self, command):
    """Original heuristic-based logic for offline use, now with advanced procedural modeling."""
    # Select target mesh if mentioned by name in command (e.g., Cylinder_0)
    for mesh_name in list(self.meshes.keys()):
        if mesh_name.lower() in command:
            self.selected_mesh_name = mesh_name
            self.update_canvas()
            break

    # Extract numbers at the very beginning to be used in all branches
    numbers = re.findall(r"[-+]?\d*\.\d+|\d+", command)
    val = float(numbers[0]) if numbers else None

    # Advanced Heuristic Geometry Compiler Offline Array & Boolean Parsers
    # A. Boolean syntax checks first: e.g., "cut Cylinder_0 from Cube_0"
    cut_match = re.search(r"(?:cut|subtract|difference)\s+(\w+)\s+(?:from|into)\s+(\w+)", command)
    if cut_match:
        tool_shape = cut_match.group(1)
        base_shape = cut_match.group(2)
        actual_tool = next((k for k in self.meshes.keys() if k.lower() == tool_shape.lower()), None)
        actual_base = next((k for k in self.meshes.keys() if k.lower() == base_shape.lower()), None)
        if actual_tool and actual_base:
            self.subtract_logic(base_name=actual_base, tool_name=actual_tool)
            return

    # E.g., "union Cylinder_0 and Cube_0" or "combine Cylinder_0 with Cube_0"
    union_match = re.search(r"(?:union|combine|join|merge)\s+(\w+)\s+(?:and|with|to)\s+(\w+)", command)
    if union_match:
        shape_a = union_match.group(1)
        shape_b = union_match.group(2)
        actual_a = next((k for k in self.meshes.keys() if k.lower() == shape_a.lower()), None)
        actual_b = next((k for k in self.meshes.keys() if k.lower() == shape_b.lower()), None)
        if actual_a and actual_b:
            self.union_logic(base_name=actual_b, tool_name=actual_a)
            return

    # E.g., "intersect Cylinder_0 and Cube_0"
    intersect_match = re.search(r"(?:intersect|intersection)\s+(\w+)\s+(?:and|with)\s+(\w+)", command)
    if intersect_match:
        shape_a = intersect_match.group(1)
        shape_b = intersect_match.group(2)
        actual_a = next((k for k in self.meshes.keys() if k.lower() == shape_a.lower()), None)
        actual_b = next((k for k in self.meshes.keys() if k.lower() == shape_b.lower()), None)
        if actual_a and actual_b:
            self.intersection_logic(base_name=actual_b, tool_name=actual_a)
            return

    # B. Array syntax checks: e.g., "grid of 3x3 cubes", "4x4 cylinder grid"
    grid_match = re.search(r"(?:grid of\s*)?(\d+)\s*[xX]\s*(\d+)\s+(\w+)", command)
    if grid_match:
        rows = int(grid_match.group(1))
        cols = int(grid_match.group(2))
        shape_name = grid_match.group(3).rstrip('s')
        shape_type = shape_name.capitalize()
        if shape_type == "Clynder": shape_type = "Cylinder"
        if shape_type == "Box": shape_type = "Cube"
        
        base_mesh = get_shape_base_mesh(self, shape_type)
        if base_mesh:
            self.save_state()
            spacing_x = base_mesh.extents[0] * 1.5
            spacing_y = base_mesh.extents[1] * 1.5
            sub_meshes = []
            for r in range(rows):
                for c in range(cols):
                    copied = base_mesh.copy()
                    tx = (c - (cols - 1) / 2) * spacing_x
                    ty = (r - (rows - 1) / 2) * spacing_y
                    copied.apply_translation([tx, ty, 0])
                    sub_meshes.append(copied)
            
            composite = trimesh.util.concatenate(sub_meshes)
            name = f"Grid_{rows}x{cols}_{shape_type}_{len(self.meshes)}"
            self.meshes[name] = composite
            self.selected_mesh_name = name
            self.reset_creative_sliders()
            self.update_canvas()
            apply_embedded_aesthetics(self, command)
            
            # Report
            msg = f"Generated a {rows}x{cols} grid of {shape_type}s offline!"
            self.chat_history.append(f"<b>AI:</b> {msg}"); self.speak(msg)
            return

    # "circle of 8 spheres", "circular array of 12 cylinders"
    circle_match = re.search(r"(?:circle of|ring of|circular array of)\s+(\d+)\s+(\w+)", command)
    if circle_match:
        count = int(circle_match.group(1))
        shape_name = circle_match.group(2).rstrip('s')
        shape_type = shape_name.capitalize()
        if shape_type == "Clynder": shape_type = "Cylinder"
        if shape_type == "Box": shape_type = "Cube"
        
        base_mesh = get_shape_base_mesh(self, shape_type)
        if base_mesh:
            self.save_state()
            radius = max(base_mesh.extents[0], base_mesh.extents[1]) * count / np.pi * 0.8
            sub_meshes = []
            for i in range(count):
                angle = i * (2 * np.pi / count)
                copied = base_mesh.copy()
                copied.apply_transform(trimesh.transformations.rotation_matrix(angle, [0, 0, 1]))
                tx = radius * np.cos(angle)
                ty = radius * np.sin(angle)
                copied.apply_translation([tx, ty, 0])
                sub_meshes.append(copied)
                
            composite = trimesh.util.concatenate(sub_meshes)
            name = f"Circle_{count}_{shape_type}_{len(self.meshes)}"
            self.meshes[name] = composite
            self.selected_mesh_name = name
            self.reset_creative_sliders()
            self.update_canvas()
            apply_embedded_aesthetics(self, command)
            
            msg = f"Generated a circular ring of {count} {shape_type}s offline!"
            self.chat_history.append(f"<b>AI:</b> {msg}"); self.speak(msg)
            return

    # "line of 5 cylinders", "row of 6 cubes"
    line_match = re.search(r"(?:line of|row of)\s+(\d+)\s+(\w+)", command)
    if line_match:
        count = int(line_match.group(1))
        shape_name = line_match.group(2).rstrip('s')
        shape_type = shape_name.capitalize()
        if shape_type == "Clynder": shape_type = "Cylinder"
        if shape_type == "Box": shape_type = "Cube"
        
        base_mesh = get_shape_base_mesh(self, shape_type)
        if base_mesh:
            self.save_state()
            spacing = base_mesh.extents[0] * 1.5
            sub_meshes = []
            for i in range(count):
                copied = base_mesh.copy()
                tx = (i - (count - 1) / 2) * spacing
                copied.apply_translation([tx, 0, 0])
                sub_meshes.append(copied)
                
            composite = trimesh.util.concatenate(sub_meshes)
            name = f"Line_{count}_{shape_type}_{len(self.meshes)}"
            self.meshes[name] = composite
            self.selected_mesh_name = name
            self.reset_creative_sliders()
            self.update_canvas()
            apply_embedded_aesthetics(self, command)
            
            msg = f"Generated a line row of {count} {shape_type}s offline!"
            self.chat_history.append(f"<b>AI:</b> {msg}"); self.speak(msg)
            return

    # "stack of 5 cylinders", "tower of 4 boxes"
    stack_match = re.search(r"(?:stack of|tower of)\s+(\d+)\s+(\w+)", command)
    if stack_match:
        count = int(stack_match.group(1))
        shape_name = stack_match.group(2).rstrip('s')
        shape_type = shape_name.capitalize()
        if shape_type == "Clynder": shape_type = "Cylinder"
        if shape_type == "Box": shape_type = "Cube"
        
        base_mesh = get_shape_base_mesh(self, shape_type)
        if base_mesh:
            self.save_state()
            sub_meshes = []
            current_height = 0.0
            for i in range(count):
                copied = base_mesh.copy()
                scale_factor = 1.0 - (i * 0.1)
                if scale_factor < 0.2: scale_factor = 0.2
                copied.apply_transform(np.diag([scale_factor, scale_factor, scale_factor, 1.0]))
                z_min = copied.bounds[0][2]
                copied.apply_translation([0, 0, current_height - z_min])
                current_height += (copied.bounds[1][2] - copied.bounds[0][2])
                sub_meshes.append(copied)
                
            composite = trimesh.util.concatenate(sub_meshes)
            name = f"Stack_{count}_{shape_type}_{len(self.meshes)}"
            self.meshes[name] = composite
            self.selected_mesh_name = name
            self.reset_creative_sliders()
            self.update_canvas()
            apply_embedded_aesthetics(self, command)
            
            msg = f"Generated a stacked tower of {count} {shape_type}s offline!"
            self.chat_history.append(f"<b>AI:</b> {msg}"); self.speak(msg)
            return

    # 1. Procedural Assembly Creation
    if "chair" in command:
        self.save_state()
        mesh = generate_procedural_chair(self)
        name = f"Procedural_Chair_{len(self.meshes)}"
        self.meshes[name] = mesh
        self.selected_mesh_name = name
        self.reset_creative_sliders()
        self.update_canvas()
        msg = "Procedurally generated a 3D Chair for you!"
        self.chat_history.append(f"<b>AI:</b> {msg}"); self.speak(msg)
        return
    elif "table" in command:
        self.save_state()
        mesh = generate_procedural_table(self)
        name = f"Procedural_Table_{len(self.meshes)}"
        self.meshes[name] = mesh
        self.selected_mesh_name = name
        self.reset_creative_sliders()
        self.update_canvas()
        msg = "Procedurally generated a 3D Table for you!"
        self.chat_history.append(f"<b>AI:</b> {msg}"); self.speak(msg)
        return
    elif "stair" in command:
        self.save_state()
        mesh = generate_procedural_staircase(self)
        name = f"Procedural_Stairs_{len(self.meshes)}"
        self.meshes[name] = mesh
        self.selected_mesh_name = name
        self.reset_creative_sliders()
        self.update_canvas()
        msg = "Procedurally generated a 3D Staircase for you!"
        self.chat_history.append(f"<b>AI:</b> {msg}"); self.speak(msg)
        return
    elif "house" in command:
        self.save_state()
        mesh = generate_procedural_house(self)
        name = f"Procedural_House_{len(self.meshes)}"
        self.meshes[name] = mesh
        self.selected_mesh_name = name
        self.reset_creative_sliders()
        self.update_canvas()
        msg = "Procedurally generated a 3D House for you!"
        self.chat_history.append(f"<b>AI:</b> {msg}"); self.speak(msg)
        return
    elif "gear" in command:
        self.save_state()
        mesh = generate_procedural_gear(self)
        name = f"Procedural_Gear_{len(self.meshes)}"
        self.meshes[name] = mesh
        self.selected_mesh_name = name
        self.reset_creative_sliders()
        self.update_canvas()
        msg = "Procedurally generated a 3D Gear for you!"
        self.chat_history.append(f"<b>AI:</b> {msg}"); self.speak(msg)
        return
    elif "mug" in command or "cup" in command:
        self.save_state()
        mesh = generate_procedural_mug(self)
        name = f"Procedural_Mug_{len(self.meshes)}"
        self.meshes[name] = mesh
        self.selected_mesh_name = name
        self.reset_creative_sliders()
        self.update_canvas()
        msg = "Procedurally generated a 3D Mug for you!"
        self.chat_history.append(f"<b>AI:</b> {msg}"); self.speak(msg)
        return
    elif "vase" in command:
        self.save_state()
        mesh = generate_procedural_vase(self)
        name = f"Procedural_Vase_{len(self.meshes)}"
        self.meshes[name] = mesh
        self.selected_mesh_name = name
        self.reset_creative_sliders()
        self.update_canvas()
        msg = "Procedurally generated a 3D Vase for you!"
        self.chat_history.append(f"<b>AI:</b> {msg}"); self.speak(msg)
        return

    # Procedural Math Art Creations Offline
    for math_type in ["mobius", "klein", "gyroid", "lorenz", "sierpinski", "dna", "wave", "ripple"]:
        if math_type in command or (any(k in command for k in ["math", "fractal", "art", "chaos"]) and math_type in command):
            add_math_shape(self, math_type)
            return

    # Custom Procedural Primitives Offline
    if "spring" in command or "helix" in command:
        self.save_state()
        mesh = generate_procedural_helix(self)
        name = f"Procedural_Helix_{len(self.meshes)}"
        self.meshes[name] = mesh
        self.selected_mesh_name = name
        self.reset_creative_sliders()
        self.update_canvas()
        msg = "Procedurally generated a 3D Helix/Spring stand!"
        self.chat_history.append(f"<b>AI:</b> {msg}"); self.speak(msg)
        return
    if "knot" in command:
        self.save_state()
        mesh = generate_procedural_torus_knot(self)
        name = f"Procedural_Torus_Knot_{len(self.meshes)}"
        self.meshes[name] = mesh
        self.selected_mesh_name = name
        self.reset_creative_sliders()
        self.update_canvas()
        msg = "Procedurally generated a trefoil Torus Knot!"
        self.chat_history.append(f"<b>AI:</b> {msg}"); self.speak(msg)
        return
    if "star" in command:
        self.save_state()
        mesh = generate_procedural_star(self)
        name = f"Procedural_Star_{len(self.meshes)}"
        self.meshes[name] = mesh
        self.selected_mesh_name = name
        self.reset_creative_sliders()
        self.update_canvas()
        msg = "Procedurally generated a 3D Star shape!"
        self.chat_history.append(f"<b>AI:</b> {msg}"); self.speak(msg)
        return
    if "heart" in command:
        self.save_state()
        mesh = generate_procedural_heart(self)
        name = f"Procedural_Heart_{len(self.meshes)}"
        self.meshes[name] = mesh
        self.selected_mesh_name = name
        self.reset_creative_sliders()
        self.update_canvas()
        msg = "Procedurally generated a 3D Heart model!"
        self.chat_history.append(f"<b>AI:</b> {msg}"); self.speak(msg)
        return

    # 2. Standard Primitive Creation Checks
    for shape in ["Cube", "Sphere", "Cylinder", "Cone", "Pyramid", "Torus", "Capsule", "Annulus", "Bolt", "Nut"]:
        if shape.lower() in command or (any(k in command for k in ["make", "create", "add", "new", "put", "spawn", "design"]) and shape.lower() in command):
            self.save_state()
            self.add_primitive(shape)
            msg = f"Created a new {shape} for you. How else can I help?"
            self.chat_history.append(f"<b>AI:</b> {msg}"); self.speak(msg)
            return

    # Shader/Aesthetic Material Application Offline
    for style in ["gold", "chrome", "glass", "neon", "clay", "default"]:
        if style in command and any(k in command for k in ["apply", "shader", "material", "style", "set"]):
            self.get_active_mesh()
            self.apply_aesthetic_shader(style)
            msg = f"Applied {style} material shader styling."
            self.chat_history.append(f"<b>AI:</b> {msg}"); self.speak(msg)
            return

    # Paint / Color Offline
    if "color" in command or "paint" in command or "gradient" in command:
        self.get_active_mesh()
        colors = {
            "red": QtGui.QColor("red"),
            "blue": QtGui.QColor("blue"),
            "green": QtGui.QColor("green"),
            "cyan": QtGui.QColor("cyan"),
            "magenta": QtGui.QColor("magenta"),
            "yellow": QtGui.QColor("yellow"),
            "black": QtGui.QColor("black"),
            "white": QtGui.QColor("white"),
            "orange": QtGui.QColor("orange"),
            "purple": QtGui.QColor("purple"),
            "pink": QtGui.QColor("pink"),
            "gold": QtGui.QColor("#d4af37"),
            "silver": QtGui.QColor("#c0c0c0"),
        }
        matched_color = None
        color_name = "custom"
        for name_key, qcolor in colors.items():
            if name_key in command:
                matched_color = qcolor
                color_name = name_key
                break
        if matched_color:
            self.current_colors[0] = matched_color
            self.current_colors[1] = matched_color
            if hasattr(self, 'c1_btn') and hasattr(self, 'c2_btn'):
                self.c1_btn.setStyleSheet(f"background-color: {matched_color.name()}; height: 30px;")
                self.c2_btn.setStyleSheet(f"background-color: {matched_color.name()}; height: 30px;")
            self.apply_color_bond()
            msg = f"Painted selected shape with {color_name}."
            self.chat_history.append(f"<b>AI:</b> {msg}"); self.speak(msg)
            return

    # Booleans Offline
    if "union" in command or "combine" in command or "join" in command:
        self.get_active_mesh()
        self.union_logic()
        return
    if "subtract" in command or "difference" in command or "cut" in command:
        self.get_active_mesh()
        self.subtract_logic()
        return
    if "intersect" in command or "intersection" in command:
        self.get_active_mesh()
        self.intersection_logic()
        return

    # Spatial Move / Translation Logic
    move_keywords = ["move", "translate", "shift", "nudge", "position"]
    if any(kw in command for kw in move_keywords):
        self.get_active_mesh()
        current_mesh = self.meshes[self.selected_mesh_name]
        move_val = val if val is not None else 10.0
        if any(neg in command for neg in ["down", "left", "back", "negative", "minus", "below"]):
            move_val = -abs(move_val)
            
        trans = [0.0, 0.0, 0.0]
        axis = "Z"
        if "x" in command or "left" in command or "right" in command or "width" in command or "sideways" in command:
            trans[0] = move_val
            axis = "X"
        elif "y" in command or "forward" in command or "backward" in command or "depth" in command or "front" in command or "back" in command:
            trans[1] = move_val
            axis = "Y"
        else: # Default to Z (up/down)
            trans[2] = move_val
            axis = "Z"
            
        self.save_state()
        current_mesh.apply_translation(trans)
        self.update_canvas()
        msg = f"Moved '{self.selected_mesh_name}' along {axis} axis by {move_val}mm."
        self.chat_history.append(f"<b>AI:</b> {msg}"); self.speak(msg)
        return

    # In-place Rotation Logic
    rotate_keywords = ["rotate", "spin", "turn", "tilt"]
    if any(kw in command for kw in rotate_keywords):
        self.get_active_mesh()
        current_mesh = self.meshes[self.selected_mesh_name]
        rot_angle = val if val is not None else 45.0
        rad = np.radians(rot_angle)
        
        axis_vec = [0.0, 0.0, 1.0] # Default to Z
        axis_name = "Z"
        if "x" in command or "pitch" in command:
            axis_vec = [1.0, 0.0, 0.0]
            axis_name = "X"
        elif "y" in command or "roll" in command:
            axis_vec = [0.0, 1.0, 0.0]
            axis_name = "Y"
            
        self.save_state()
        centroid = current_mesh.centroid.copy()
        current_mesh.apply_translation(-centroid)
        current_mesh.apply_transform(trimesh.transformations.rotation_matrix(rad, axis_vec))
        current_mesh.apply_translation(centroid)
        self.update_canvas()
        msg = f"Rotated '{self.selected_mesh_name}' by {rot_angle}° around {axis_name} axis."
        self.chat_history.append(f"<b>AI:</b> {msg}"); self.speak(msg)
        return

    # Deletion and Scene Clearing Logic
    if any(kw in command for kw in ["clear scene", "delete all", "empty scene", "remove all"]):
        self.save_state()
        self.meshes.clear()
        self.selected_mesh_name = None
        self.update_canvas()
        msg = "Cleared the entire workspace."
        self.chat_history.append(f"<b>AI:</b> {msg}"); self.speak(msg)
        return

    if "delete" in command or "remove" in command:
        if self.selected_mesh_name:
            name = self.selected_mesh_name
            self.delete_selected()
            msg = f"Deleted shape '{name}' from scene."
            self.chat_history.append(f"<b>AI:</b> {msg}"); self.speak(msg)
        else:
            msg = "Nothing selected to delete."
            self.chat_history.append(f"<b>AI:</b> {msg}"); self.speak(msg)
        return

    # Laplacian Smoothing Logic
    if "smooth" in command or "laplacian" in command:
        self.get_active_mesh()
        current_mesh = self.meshes[self.selected_mesh_name]
        self.save_state()
        iterations = int(val) if val is not None else 3
        trimesh.smoothing.filter_laplacian(current_mesh, iterations=iterations)
        self.update_canvas()
        msg = f"Applied {iterations} iterations of Laplacian smoothing to '{self.selected_mesh_name}'."
        self.chat_history.append(f"<b>AI:</b> {msg}"); self.speak(msg)
        return

    # Subdivision Logic
    if "subdivide" in command or "subdivision" in command:
        self.get_active_mesh()
        current_mesh = self.meshes[self.selected_mesh_name]
        self.save_state()
        sub_level = int(val) if val is not None else 1
        for _ in range(sub_level):
            current_mesh = current_mesh.subdivide()
        self.meshes[self.selected_mesh_name] = current_mesh
        self.update_canvas()
        msg = f"Subdivided '{self.selected_mesh_name}' geometry by {sub_level} levels."
        self.chat_history.append(f"<b>AI:</b> {msg}"); self.speak(msg)
        return

    # Selection management
    if "clear selection" in command or "deselect" in command:
        self.selected_mesh_name = None
        self.update_canvas()
        msg = "Deselected all shapes."
        self.chat_history.append(f"<b>AI:</b> {msg}"); self.speak(msg)
        return

    # Creative slider resetting
    if "reset sliders" in command or "reset creative" in command:
        self.reset_creative_sliders()
        msg = "Reset all creative deformer sliders."
        self.chat_history.append(f"<b>AI:</b> {msg}"); self.speak(msg)
        return

    # Stable Pose & Drop Bed Offline
    if "drop" in command or "bed" in command or "z=0" in command or "ground" in command:
        self.get_active_mesh()
        self.drop_to_bed_selected()
        msg = "Dropped selected part to the Z=0 build plate."
        self.chat_history.append(f"<b>AI:</b> {msg}"); self.speak(msg)
        return
    if "stable" in command or "orient" in command:
        self.get_active_mesh()
        self.orient_selected_stable()
        msg = "Oriented selected part to its most stable pose on the build bed."
        self.chat_history.append(f"<b>AI:</b> {msg}"); self.speak(msg)
        return
    if "align" in command:
        self.align_selected_dialog()
        return

    # Deformers Offline
    if "twist" in command:
        self.get_active_mesh("Cylinder")
        angle = val if val is not None else 45.0
        self.creative_mode_active.setChecked(True)
        self.creative_twist.setValue(int(angle))
        self.apply_creative_deforms()
        msg = f"Applied twist deformation of {angle} degrees."
        self.chat_history.append(f"<b>AI:</b> {msg}"); self.speak(msg)
        return
    if "taper" in command:
        self.get_active_mesh("Cone")
        factor = val if val is not None else 1.5
        self.creative_mode_active.setChecked(True)
        self.creative_taper.setValue(int(factor * 100))
        self.apply_creative_deforms()
        msg = f"Applied taper deformation with factor {factor}."
        self.chat_history.append(f"<b>AI:</b> {msg}"); self.speak(msg)
        return
    if "bend" in command:
        self.get_active_mesh("Cylinder")
        angle = val if val is not None else 30.0
        self.creative_mode_active.setChecked(True)
        self.creative_bend.setValue(int(angle))
        self.apply_creative_deforms()
        msg = f"Applied bend deformation of {angle} degrees."
        self.chat_history.append(f"<b>AI:</b> {msg}"); self.speak(msg)
        return
    if "bulge" in command or "swell" in command:
        self.get_active_mesh("Sphere")
        factor = val if val is not None else 0.3
        self.creative_mode_active.setChecked(True)
        self.creative_bulge.setValue(int(factor * 100))
        self.apply_creative_deforms()
        msg = f"Applied bulge/swell deformation with factor {factor}."
        self.chat_history.append(f"<b>AI:</b> {msg}"); self.speak(msg)
        return
    if "noise" in command or "ruffles" in command or "organic" in command:
        self.get_active_mesh("Cube")
        factor = val if val is not None else 1.0
        self.creative_mode_active.setChecked(True)
        self.creative_noise.setValue(int(factor * 10))
        self.apply_creative_deforms()
        msg = f"Applied organic noise deformation with factor {factor}."
        self.chat_history.append(f"<b>AI:</b> {msg}"); self.speak(msg)
        return

    # Figurine / Photo Requirement Logic
    if any(k in command for k in ["what do you need", "how many photos", "figurine"]):
        msg = "To create a perfect figurine, I need 8 photos total."
        self.chat_history.append(f"<b>AI:</b> {msg}<br>"
                                 "1. Front, Back, Left, Right (Eye level)<br>"
                                 "2. Four 45-degree corner shots<br>"
                                 "3. One Top-Down shot (optional but recommended).")
        self.speak(msg)
        return

    # Global AI Utilities
    if "remove background" in command or "clear background" in command:
        self.remove_background_ai()
        return

    # 3. Smart Selection / Creation Fallback
    if not self.selected_mesh_name:
        if self.meshes:
            self.selected_mesh_name = list(self.meshes.keys())[-1]
            self.update_canvas()
            self.chat_history.append(f"<b>AI:</b> No part was selected, so I automatically selected '{self.selected_mesh_name}' to modify.")
        else:
            self.save_state()
            self.add_primitive("Cube")
            msg = "No shapes exist in the scene. I created a new Cube for you to start!"
            self.chat_history.append(f"<b>AI:</b> {msg}"); self.speak(msg)
            if not any(k in command for k in ["make", "create", "add", "new"]):
                pass 

    current_mesh = self.meshes[self.selected_mesh_name]
    modified = False

    # 5. Smart Texture Mapping (Auto-recognizes all 20 patterns)
    for tex_name in self.pattern_functions.keys():
        if tex_name.lower() in command:
            self.apply_texture_by_name(tex_name)
            return

    # 6. Smart Mirror/Duplicate
    if "duplicate" in command or "copy" in command:
        self.duplicate_selected(); return
    if "mirror" in command or "flip" in command:
        current_mesh.apply_transform(trimesh.transformations.reflection_matrix([0,0,0], [1,0,0]))
        self.chat_history.append("<b>AI:</b> Mirrored the object.")
        modified = True

    # 7. Scaling Logic
    scale_matrix = np.eye(4)
    if "wide" in command or "width" in command or "stretch" in command:
        factor = val if val is not None else 1.25
        scale_matrix[0, 0] = factor
        self.chat_history.append(f"<b>AI:</b> Adjusting width (X-axis) by factor {factor}.")
        modified = True
    if "deep" in command or "depth" in command:
        factor = val if val is not None else 1.25
        scale_matrix[1, 1] = factor
        self.chat_history.append(f"<b>AI:</b> Adjusting depth (Y-axis) by factor {factor}.")
        modified = True
    if "tall" in command or "height" in command or "high" in command or "long" in command:
        factor = val if val is not None else 1.25
        scale_matrix[2, 2] = factor
        self.chat_history.append(f"<b>AI:</b> Adjusting height (Z-axis) by factor {factor}.")
        modified = True
    if "scale" in command or "size" in command or "bigger" in command or "smaller" in command:
        factor = val if val is not None else 1.2
        if "smaller" in command or "shrink" in command:
            factor = 1.0 / factor
        scale_matrix[:3, :3] *= factor
        self.chat_history.append(f"<b>AI:</b> Scaling overall size by factor {factor:.2f}.")
        modified = True

    if modified:
        self.save_state()
        centroid = current_mesh.centroid.copy()
        current_mesh.apply_translation(-centroid)
        current_mesh.apply_transform(scale_matrix)
        current_mesh.apply_translation(centroid)
        self.update_canvas()
        self.speak("Geometry updated offline.")

    # Default fallback: Treat unrecognized descriptive commands or commands with creation keywords as text-to-3D prompts
    if len(command.split()) >= 3 or any(verb in command for verb in ["make", "create", "generate", "build", "synthesize", "design", "draw", "render", "pose"]):
        self.generate_3d_from_text(command)
        return

def add_math_shape(self, shape_type):
    """Generates mathematical art models and updates the active scene."""
    self.save_state()
    self.chat_history.append(f"<b>System:</b> Plotting Mathematical Art structure '{shape_type}'...")
    if shape_type == "mobius":
        mesh = create_mobius_strip(self)
        name = f"Math_Mobius_{len(self.meshes)}"
    elif shape_type == "klein":
        mesh = create_klein_bottle(self)
        name = f"Math_Klein_{len(self.meshes)}"
    elif shape_type == "gyroid":
        mesh = create_gyroid_infill(self)
        name = f"Math_Gyroid_{len(self.meshes)}"
    elif shape_type == "lorenz":
        mesh = create_lorenz_attractor(self)
        name = f"Math_Lorenz_{len(self.meshes)}"
    elif shape_type == "sierpinski":
        mesh = create_sierpinski_pyramid(self)
        name = f"Math_Sierpinski_{len(self.meshes)}"
    elif shape_type == "dna":
        mesh = create_dna_helix(self)
        name = f"Math_DNA_{len(self.meshes)}"
    elif shape_type in ["wave", "ripple"]:
        mesh = create_wave_surface(self)
        name = f"Math_Wave_{len(self.meshes)}"
    else:
        return

    # Snap to print bed (Z=0)
    mesh.apply_translation([0, 0, -mesh.bounds[0][2]])
    self.meshes[name] = mesh
    self.selected_mesh_name = name
    self.reset_creative_sliders()
    self.update_canvas()
    self.chat_history.append(f"<b>System:</b> Mathematical shape '{name}' added to scene.")

def create_mobius_strip(self, r=25, w=8, slices=80):
    """Generates a parametric Möbius strip mesh."""
    u = np.linspace(0, 2 * np.pi, slices)
    v = np.linspace(-w/2, w/2, 10)
    U, V = np.meshgrid(u, v)
    x = (r + V * np.cos(U / 2)) * np.cos(U)
    y = (r + V * np.cos(U / 2)) * np.sin(U)
    z = V * np.sin(U / 2)
    vertices = np.vstack([x.ravel(), y.ravel(), z.ravel()]).T
    faces = []
    rows, cols = x.shape
    for r_idx in range(rows - 1):
        for c_idx in range(cols - 1):
            p0 = r_idx * cols + c_idx
            p1 = r_idx * cols + c_idx + 1
            p2 = (r_idx + 1) * cols + c_idx
            p3 = (r_idx + 1) * cols + c_idx + 1
            faces.append([p0, p1, p3])
            faces.append([p0, p3, p2])
    return trimesh.Trimesh(vertices=vertices, faces=faces)

def create_klein_bottle(self, scale=1.5, slices=60):
    """Generates a figure-8 immersion Klein bottle mesh."""
    u = np.linspace(0, 2*np.pi, slices)
    v = np.linspace(0, 2*np.pi, slices)
    U, V = np.meshgrid(u, v)
    x = scale * (6*np.cos(U)*(1 + np.sin(U)) + 4*(1 - np.cos(U)/2)*np.cos(U)*np.cos(V))
    y = scale * (16*np.sin(U) + 4*(1 - np.cos(U)/2)*np.sin(U)*np.cos(V))
    z = scale * (4*(1 - np.cos(U)/2)*np.sin(V))
    vertices = np.vstack([x.ravel(), y.ravel(), z.ravel()]).T
    faces = []
    rows, cols = x.shape
    for r_idx in range(rows - 1):
        for c_idx in range(cols - 1):
            p0 = r_idx * cols + c_idx
            p1 = r_idx * cols + c_idx + 1
            p2 = (r_idx + 1) * cols + c_idx
            p3 = (r_idx + 1) * cols + c_idx + 1
            faces.append([p0, p1, p3])
            faces.append([p0, p3, p2])
    return trimesh.Trimesh(vertices=vertices, faces=faces)

def create_gyroid_infill(self, bounds_sz=40, grid_res=None, iso=0.0):
    """Generates a periodic Gyroid infill slice using marching cubes."""
    if grid_res is None:
        grid_res = getattr(self, 'grid_resolution', 25)
    try:
        from skimage import measure
        x = np.linspace(-np.pi*1.8, np.pi*1.8, grid_res)
        y = np.linspace(-np.pi*1.8, np.pi*1.8, grid_res)
        z = np.linspace(-np.pi*1.8, np.pi*1.8, grid_res)
        X, Y, Z = np.meshgrid(x, y, z, indexing='ij')
        values = np.sin(X)*np.cos(Y) + np.sin(Y)*np.cos(Z) + np.sin(Z)*np.cos(X)
        verts, faces, normals, vals = measure.marching_cubes(values, level=iso)
        verts = (verts / grid_res - 0.5) * bounds_sz
        return trimesh.Trimesh(vertices=verts, faces=faces)
    except Exception:
        return trimesh.creation.torus(major_radius=20, minor_radius=5)

def create_lorenz_attractor(self, dt=0.015, steps=1500, sigma=10, rho=28, beta=8/3):
    """Generates a chaotic 3D ribbon along the Lorenz Attractor path."""
    x, y, z = 0.1, 0.0, 0.0
    points = []
    for _ in range(steps):
        dx = sigma * (y - x) * dt
        dy = (x * (rho - z) - y) * dt
        dz = (x * y - beta * z) * dt
        x += dx
        y += dy
        z += dz
        points.append([x, y, z])
    points = np.array(points)
    vertices = []
    faces = []
    width = 2.5
    for i in range(len(points) - 1):
        p = points[i]
        dir_v = points[i+1] - p
        dir_norm = np.linalg.norm(dir_v)
        if dir_norm > 0:
            dir_v /= dir_norm
        trans = np.cross(dir_v, [0,0,1])
        t_norm = np.linalg.norm(trans)
        if t_norm > 0:
            trans /= t_norm
        vertices.append(p - trans * width/2)
        vertices.append(p + trans * width/2)
    for i in range(len(points) - 2):
        p0 = 2 * i
        p1 = 2 * i + 1
        p2 = 2 * (i + 1)
        p3 = 2 * (i + 1) + 1
        faces.append([p0, p1, p3])
        faces.append([p0, p3, p2])
    mesh = trimesh.Trimesh(vertices=np.array(vertices), faces=np.array(faces))
    mesh.apply_translation(-mesh.centroid)
    mesh.apply_transform(np.diag([0.65, 0.65, 0.65, 1.0]))
    return mesh

def create_sierpinski_pyramid(self, level=3, size=40):
    """Generates a recursive 3D Sierpinski fractal tetrahedron mesh."""
    def get_tetrahedron(p0, p1, p2, p3):
        verts = np.array([p0, p1, p2, p3])
        faces = [[0, 1, 2], [0, 2, 3], [0, 3, 1], [1, 3, 2]]
        return trimesh.Trimesh(vertices=verts, faces=faces)
        
    def recurse(p0, p1, p2, p3, lvl):
        if lvl == 0:
            return [get_tetrahedron(p0, p1, p2, p3)]
        m01 = (p0 + p1) / 2
        m02 = (p0 + p2) / 2
        m03 = (p0 + p3) / 2
        m12 = (p1 + p2) / 2
        m13 = (p1 + p3) / 2
        m23 = (p2 + p3) / 2
        t1 = recurse(p0, m01, m02, m03, lvl - 1)
        t2 = recurse(m01, p1, m12, m13, lvl - 1)
        t3 = recurse(m02, m12, p2, m23, lvl - 1)
        t4 = recurse(m03, m13, m23, p3, lvl - 1)
        return t1 + t2 + t3 + t4
        
    h = size * np.sqrt(2/3)
    p0 = np.array([0, 0, h])
    p1 = np.array([-size/2, -size / (2 * np.sqrt(3)), 0])
    p2 = np.array([size/2, -size / (2 * np.sqrt(3)), 0])
    p3 = np.array([0, size / np.sqrt(3), 0])
    meshes = recurse(p0, p1, p2, p3, level)
    return trimesh.util.concatenate(meshes)

def create_dna_helix(self, radius=12, pitch=15, coils=2, thickness=1.8):
    """Generates a parametric double helix DNA structure with cross ladder rungs."""
    total_angle = coils * 2 * np.pi
    slices = 60
    t = np.linspace(0, total_angle, slices)
    sub_meshes = []
    
    # Build Strand A and Strand B
    for i in range(slices):
        t_val = t[i]
        # Strand A
        ax = radius * np.cos(t_val)
        ay = radius * np.sin(t_val)
        az = (pitch / (2 * np.pi)) * t_val
        
        # Strand B
        bx = radius * np.cos(t_val + np.pi)
        by = radius * np.sin(t_val + np.pi)
        bz = az
        
        sub_meshes.append(trimesh.creation.icosphere(radius=thickness * 1.5).apply_translation([ax, ay, az]))
        sub_meshes.append(trimesh.creation.icosphere(radius=thickness * 1.5).apply_translation([bx, by, bz]))
        
        # Draw cross rung every 3 slices
        if i % 3 == 0:
            rung = trimesh.creation.cylinder(radius=thickness*0.6, height=radius*2)
            rung.apply_transform(trimesh.transformations.rotation_matrix(t_val, [0,0,1]))
            rung.apply_translation([0, 0, az])
            sub_meshes.append(rung)
            
    return trimesh.util.concatenate(sub_meshes)

def create_wave_surface(self, bounds_sz=50, waves=3.0, amp=5.0):
    """Generates a math ripple wave surface."""
    grid_res = 40
    u = np.linspace(-bounds_sz/2, bounds_sz/2, grid_res)
    v = np.linspace(-bounds_sz/2, bounds_sz/2, grid_res)
    U, V = np.meshgrid(u, v)
    U = U.flatten()
    V = V.flatten()
    R = np.sqrt(U**2 + V**2)
    Z = amp * np.sin(waves * R / (bounds_sz/2))
    vertices = np.column_stack((U, V, Z))
    
    faces = []
    for i in range(grid_res - 1):
        for j in range(grid_res - 1):
            idx = i * grid_res + j
            faces.append([idx, idx + 1, idx + grid_res])
            faces.append([idx + 1, idx + grid_res + 1, idx + grid_res])
            
    return trimesh.Trimesh(vertices=vertices, faces=np.array(faces))

def get_shape_base_mesh(self, shape_type):
    """Returns a baseline trimesh geometry by type for offline compilation."""
    if shape_type == "Cube":
        return trimesh.creation.box(extents=[40, 40, 40])
    elif shape_type == "Sphere":
        return trimesh.creation.icosphere(radius=20)
    elif shape_type == "Cylinder":
        return trimesh.creation.cylinder(radius=20, height=40)
    elif shape_type == "Cone":
        return trimesh.creation.cone(radius=20, height=40)
    elif shape_type == "Pyramid":
        return trimesh.creation.cone(radius=20, height=40, sections=4)
    elif shape_type == "Torus":
        return trimesh.creation.torus(major_radius=20, minor_radius=5)
    elif shape_type == "Capsule":
        return trimesh.creation.capsule(radius=10, height=40)
    elif shape_type == "Annulus":
        return trimesh.creation.annulus(inner_radius=10, outer_radius=20, height=10)
    elif shape_type == "Helix":
        return generate_procedural_helix(self)
    elif shape_type == "Star":
        return generate_procedural_star(self)
    elif shape_type == "Heart":
        return generate_procedural_heart(self)
    elif shape_type == "Chair":
        return generate_procedural_chair(self)
    elif shape_type == "Table":
        return generate_procedural_table(self)
    elif shape_type == "House":
        return generate_procedural_house(self)
    elif shape_type == "Gear":
        return generate_procedural_gear(self)
    elif shape_type == "Mug" or shape_type == "Cup":
        return generate_procedural_mug(self)
    elif shape_type == "Vase":
        return generate_procedural_vase(self)
    return None

def apply_embedded_aesthetics(self, command):
    """Helper to apply shaders and colors directly inside composite offline creation commands."""
    for style in ["gold", "chrome", "glass", "neon", "clay"]:
        if style in command:
            self.apply_aesthetic_shader(style)
            break
    colors = {
        "red": QtGui.QColor("red"),
        "blue": QtGui.QColor("blue"),
        "green": QtGui.QColor("green"),
        "cyan": QtGui.QColor("cyan"),
        "magenta": QtGui.QColor("magenta"),
        "yellow": QtGui.QColor("yellow"),
        "orange": QtGui.QColor("orange"),
        "purple": QtGui.QColor("purple"),
        "pink": QtGui.QColor("pink"),
        "gold": QtGui.QColor("#d4af37"),
        "silver": QtGui.QColor("#c0c0c0"),
    }
    for name_key, qcolor in colors.items():
        if name_key in command:
            self.current_colors[0] = qcolor
            self.current_colors[1] = qcolor
            if hasattr(self, 'c1_btn') and hasattr(self, 'c2_btn'):
                self.c1_btn.setStyleSheet(f"background-color: {qcolor.name()}; height: 30px;")
                self.c2_btn.setStyleSheet(f"background-color: {qcolor.name()}; height: 30px;")
            self.apply_color_bond()
            break

def generate_procedural_chair(self, seat_w=40, seat_d=40, seat_h=4, leg_r=2, leg_h=30, back_h=35):
    """Procedurally builds a watertight 3D Chair mesh assembly."""
    seat = trimesh.creation.box(extents=[seat_w, seat_d, seat_h])
    seat.apply_translation([0, 0, leg_h + seat_h/2])
    
    legs = []
    offsets = [
        [-seat_w/2 + leg_r*1.5, -seat_d/2 + leg_r*1.5],
        [seat_w/2 - leg_r*1.5, -seat_d/2 + leg_r*1.5],
        [-seat_w/2 + leg_r*1.5, seat_d/2 - leg_r*1.5],
        [seat_w/2 - leg_r*1.5, seat_d/2 - leg_r*1.5]
    ]
    for ox, oy in offsets:
        leg = trimesh.creation.cylinder(radius=leg_r, height=leg_h)
        leg.apply_translation([ox, oy, leg_h/2])
        legs.append(leg)
        
    back = trimesh.creation.box(extents=[seat_w, seat_h, back_h])
    back.apply_translation([0, -seat_d/2 + seat_h/2, leg_h + seat_h + back_h/2])
    
    chair_parts = [seat, back] + legs
    return trimesh.util.concatenate(chair_parts)

def generate_procedural_table(self, top_w=80, top_d=55, top_h=5, leg_r=3, leg_h=38):
    """Procedurally builds a watertight 3D Table mesh assembly."""
    top = trimesh.creation.box(extents=[top_w, top_d, top_h])
    top.apply_translation([0, 0, leg_h + top_h/2])
    
    legs = []
    offsets = [
        [-top_w/2 + leg_r*2, -top_d/2 + leg_r*2],
        [top_w/2 - leg_r*2, -top_d/2 + leg_r*2],
        [-top_w/2 + leg_r*2, top_d/2 - leg_r*2],
        [top_w/2 - leg_r*2, top_d/2 - leg_r*2]
    ]
    for ox, oy in offsets:
        leg = trimesh.creation.cylinder(radius=leg_r, height=leg_h)
        leg.apply_translation([ox, oy, leg_h/2])
        legs.append(leg)
        
    table_parts = [top] + legs
    return trimesh.util.concatenate(table_parts)

def generate_procedural_staircase(self, steps=8, step_w=50, step_d=12, step_h=6):
    """Procedurally builds a watertight 3D Staircase step assembly."""
    stair_parts = []
    for i in range(steps):
        step = trimesh.creation.box(extents=[step_w, step_d, step_h])
        step.apply_translation([0, i * step_d, i * step_h + step_h/2])
        stair_parts.append(step)
    return trimesh.util.concatenate(stair_parts)

def generate_procedural_house(self, w=60, d=60, h=40, roof_h=22):
    """Procedurally builds a 3D House structure with a pitched triangular roof."""
    body = trimesh.creation.box(extents=[w, d, h])
    body.apply_translation([0, 0, h/2])
    
    # Pitched roof profile
    vertices = np.array([
        [-w/2, -d/2, h],
        [w/2, -d/2, h],
        [w/2, d/2, h],
        [-w/2, d/2, h],
        [0, -d/2, h + roof_h],
        [0, d/2, h + roof_h]
    ])
    faces = np.array([
        [0, 1, 4], [2, 3, 5], [1, 2, 5], [1, 5, 4],
        [3, 0, 4], [3, 4, 5], [0, 3, 2], [0, 2, 1]
    ])
    roof = trimesh.Trimesh(vertices=vertices, faces=faces)
    house_parts = [body, roof]
    return trimesh.util.concatenate(house_parts)

def generate_procedural_gear(self, r=28, h=8, teeth=14, teeth_h=3.5, center_hole_r=6):
    """Procedurally builds a watertight 3D Gear mesh with functional cogs."""
    body = trimesh.creation.cylinder(radius=r - teeth_h, height=h)
    body.apply_translation([0, 0, h/2])
    
    cog_parts = [body]
    angle_step = 2 * np.pi / teeth
    for i in range(teeth):
        angle = i * angle_step
        cog = trimesh.creation.box(extents=[teeth_h * 2, teeth_h * 1.5, h])
        cx = (r - teeth_h/2) * np.cos(angle)
        cy = (r - teeth_h/2) * np.sin(angle)
        cog.apply_translation([cx, cy, h/2])
        cog.apply_transform(trimesh.transformations.rotation_matrix(angle, [0, 0, 1], point=[cx, cy, h/2]))
        cog_parts.append(cog)
        
    solid_gear = trimesh.boolean.union(cog_parts)
    hole = trimesh.creation.cylinder(radius=center_hole_r, height=h*2)
    hole.apply_translation([0, 0, h/2])
    
    try:
        final_gear = trimesh.boolean.difference(solid_gear, hole)
    except Exception:
        final_gear = solid_gear
    return final_gear

def generate_procedural_mug(self, r=18, h=36, thickness=2.2, handle_r=11):
    """Procedurally builds a watertight 3D Coffee Mug mesh."""
    outer = trimesh.creation.cylinder(radius=r, height=h)
    outer.apply_translation([0, 0, h/2])
    
    inner = trimesh.creation.cylinder(radius=r - thickness, height=h)
    inner.apply_translation([0, 0, h/2 + thickness])
    
    try:
        cup_body = trimesh.boolean.difference(outer, inner, engine='scad')
    except Exception:
        cup_body = outer
        
    handle = trimesh.creation.torus(major_radius=handle_r, minor_radius=thickness * 0.9)
    handle.apply_transform(trimesh.transformations.rotation_matrix(np.pi/2, [1, 0, 0]))
    handle.apply_translation([r - thickness, 0, h / 2])
    
    try:
        mug = trimesh.boolean.union([cup_body, handle], engine='scad')
    except Exception:
        mug = trimesh.util.concatenate([cup_body, handle])
    return mug

def generate_procedural_vase(self, r_base=14, r_mid=24, r_neck=11, r_rim=16, h=48, thickness=2):
    """Procedurally builds a beautiful curves/lofted 3D Vase mesh."""
    slices = 28
    zs = np.linspace(0, h, slices)
    vertices = []
    faces = []
    def get_radius(t):
        return r_base * (1-t) + r_mid * np.sin(t * np.pi) + r_rim * t
    segments = 30
    for z_val in zs:
        t = z_val / h
        rad = get_radius(t)
        for j in range(segments):
            theta = j * 2 * np.pi / segments
            vertices.append([rad * np.cos(theta), rad * np.sin(theta), z_val])
    for i in range(slices - 1):
        for j in range(segments):
            p0 = i * segments + j
            p1 = i * segments + (j + 1) % segments
            p2 = (i + 1) * segments + j
            p3 = (i + 1) * segments + (j + 1) % segments
            faces.append([p0, p1, p3])
            faces.append([p0, p3, p2])
    outer_mesh = trimesh.Trimesh(vertices=vertices, faces=faces)
    inner_mesh = outer_mesh.copy()
    inner_mesh.apply_transform(np.diag([0.88, 0.88, 1.0, 1.0]))
    inner_mesh.apply_translation([0, 0, thickness])
    try:
        vase = trimesh.boolean.difference(outer_mesh, inner_mesh, engine='scad')
    except Exception:
        vase = outer_mesh
    return vase

def generate_procedural_helix(self, r=12, pitch=6, coils=6, thickness=2, segments=24, slices=120):
    """Procedurally builds a watertight 3D Spring/Helix coil mesh."""
    total_angle = coils * 2 * np.pi
    t = np.linspace(0, total_angle, slices)
    vertices = []
    faces = []
    
    for i, t_val in enumerate(t):
        cx = r * np.cos(t_val)
        cy = r * np.sin(t_val)
        cz = (pitch / (2 * np.pi)) * t_val
        
        dx = -r * np.sin(t_val)
        dy = r * np.cos(t_val)
        dz = pitch / (2 * np.pi)
        dir_v = np.array([dx, dy, dz])
        dir_v /= np.linalg.norm(dir_v)
        
        u = np.array([-np.sin(t_val), np.cos(t_val), 0])
        u /= np.linalg.norm(u)
        v = np.cross(dir_v, u)
        v /= np.linalg.norm(v)
        
        for j in range(segments):
            theta = j * 2 * np.pi / segments
            px = cx + thickness * (np.cos(theta) * u[0] + np.sin(theta) * v[0])
            py = cy + thickness * (np.cos(theta) * u[1] + np.sin(theta) * v[1])
            pz = cz + thickness * (np.cos(theta) * u[2] + np.sin(theta) * v[2])
            vertices.append([px, py, pz])
            
    for i in range(slices - 1):
        for j in range(segments):
            p0 = i * segments + j
            p1 = i * segments + (j + 1) % segments
            p2 = (i + 1) * segments + j
            p3 = (i + 1) * segments + (j + 1) % segments
            faces.append([p0, p1, p3])
            faces.append([p0, p3, p2])
            
    v_bottom = np.array([r, 0, 0])
    v_top = np.array([r * np.cos(total_angle), r * np.sin(total_angle), (pitch / (2 * np.pi)) * total_angle])
    vertices.append(v_bottom)
    vertices.append(v_top)
    
    idx_bottom = len(vertices) - 2
    idx_top = len(vertices) - 1
    
    for j in range(segments):
        p0 = j
        p1 = (j + 1) % segments
        faces.append([p1, p0, idx_bottom])
        
    start_top = (slices - 1) * segments
    for j in range(segments):
        p0 = start_top + j
        p1 = start_top + (j + 1) % segments
        faces.append([p0, p1, idx_top])
        
    return trimesh.Trimesh(vertices=np.array(vertices), faces=np.array(faces))

def generate_procedural_torus_knot(self, r_tube=1.8, r_knot=18, p=2, q=3, segments=16, slices=150):
    """Procedurally builds a 3D Torus Knot mesh."""
    t = np.linspace(0, 2 * np.pi, slices)
    vertices = []
    faces = []
    
    for i, t_val in enumerate(t):
        r = r_knot * (2 + np.sin(q * t_val)) / 2
        cx = r * np.cos(p * t_val)
        cy = r * np.sin(p * t_val)
        cz = r_knot * np.cos(q * t_val) / 2
        
        dt = 1e-4
        r_next = r_knot * (2 + np.sin(q * (t_val + dt))) / 2
        cx_next = r_next * np.cos(p * (t_val + dt))
        cy_next = r_next * np.sin(p * (t_val + dt))
        cz_next = r_knot * np.cos(q * (t_val + dt)) / 2
        dir_v = np.array([cx_next - cx, cy_next - cy, cz_next - cz])
        dir_v /= np.linalg.norm(dir_v)
        
        u = np.array([-np.sin(p * t_val), np.cos(p * t_val), 0])
        u /= np.linalg.norm(u)
        v = np.cross(dir_v, u)
        v /= np.linalg.norm(v)
        
        for j in range(segments):
            theta = j * 2 * np.pi / segments
            px = cx + r_tube * (np.cos(theta) * u[0] + np.sin(theta) * v[0])
            py = cy + r_tube * (np.cos(theta) * u[1] + np.sin(theta) * v[1])
            pz = cz + r_tube * (np.cos(theta) * u[2] + np.sin(theta) * v[2])
            vertices.append([px, py, pz])
            
    for i in range(slices - 1):
        for j in range(segments):
            p0 = i * segments + j
            p1 = i * segments + (j + 1) % segments
            p2 = (i + 1) * segments + j
            p3 = (i + 1) * segments + (j + 1) % segments
            faces.append([p0, p1, p3])
            faces.append([p0, p3, p2])
            
    start_last = (slices - 1) * segments
    for j in range(segments):
        p0 = start_last + j
        p1 = start_last + (j + 1) % segments
        p2 = j
        p3 = (j + 1) % segments
        faces.append([p0, p1, p3])
        faces.append([p0, p3, p2])
        
    return trimesh.Trimesh(vertices=np.array(vertices), faces=np.array(faces))

def generate_procedural_star(self, r_outer=25, r_inner=10, thickness=8, points=5):
    """Procedurally builds a 3D Star shape mesh."""
    vertices = []
    faces = []
    angle_step = np.pi / points
    
    vertices.append([0, 0, -thickness/2])
    vertices.append([0, 0, thickness/2])
    
    for i in range(2 * points):
        angle = i * angle_step
        r = r_outer if i % 2 == 0 else r_inner
        vertices.append([r * np.cos(angle), r * np.sin(angle), 0])
        
    num_perimeter = 2 * points
    for i in range(num_perimeter):
        p0 = 2 + i
        p1 = 2 + (i + 1) % num_perimeter
        faces.append([p1, p0, 0])
        faces.append([p0, p1, 1])
        
    return trimesh.Trimesh(vertices=np.array(vertices), faces=np.array(faces))

def generate_procedural_heart(self, size=25, thickness=8, slices=40):
    """Procedurally builds a solid watertight 3D Heart mesh."""
    t = np.linspace(0, 2*np.pi, slices)
    vertices = []
    faces = []
    
    x_2d = 16 * np.sin(t)**3
    y_2d = 13 * np.cos(t) - 5 * np.cos(2*t) - 2 * np.cos(3*t) - np.cos(4*t)
    x_2d = (x_2d - np.mean(x_2d)) / (np.max(x_2d) - np.min(x_2d)) * size
    y_2d = (y_2d - np.mean(y_2d)) / (np.max(y_2d) - np.min(y_2d)) * size
    
    vertices.append([0, np.mean(y_2d), -thickness/2])
    vertices.append([0, np.mean(y_2d), thickness/2])
    
    for i in range(slices):
        vertices.append([x_2d[i], y_2d[i], -thickness/2])
        vertices.append([x_2d[i], y_2d[i], thickness/2])
        
    for i in range(slices):
        p0 = 2 + i
        p1 = 2 + (i + 1) % slices
        p2 = 2 + slices + i
        p3 = 2 + slices + (i + 1) % slices
        faces.append([p0, p1, p3])
        faces.append([p0, p3, p2])
        
    for i in range(slices):
        p0 = 2 + i
        p1 = 2 + (i + 1) % slices
        faces.append([p1, p0, 0])
        
    for i in range(slices):
        p0 = 2 + slices + i
        p1 = 2 + slices + (i + 1) % slices
        faces.append([p0, p1, 1])
        
    mesh = trimesh.Trimesh(vertices=np.array(vertices), faces=np.array(faces))
    mesh.apply_transform(trimesh.transformations.rotation_matrix(np.pi/2, [1,0,0]))
    mesh.apply_translation([0, 0, -mesh.bounds[0][2]])
    return mesh

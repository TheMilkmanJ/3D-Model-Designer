import sys
import os
import subprocess
import importlib.util
import traceback

# Setup Error Logging immediately at startup (console & file)
log_dir = os.path.dirname(os.path.abspath(__file__)) if __file__ else os.getcwd()
error_log_path = os.path.join(log_dir, "error_log.txt")

class DualLogger:
    def __init__(self, filepath, stream):
        self.filepath = filepath
        self.stream = stream
    def write(self, message):
        self.stream.write(message)
        self.stream.flush()
        try:
            with open(self.filepath, "a", encoding="utf-8") as f:
                f.write(message)
        except Exception:
            pass
    def flush(self):
        self.stream.flush()

try:
    sys.stderr = DualLogger(error_log_path, sys.stderr)
    sys.stdout = DualLogger(error_log_path, sys.stdout)
except Exception:
    pass

def log_exception(exc_type, exc_value, exc_traceback):
    try:
        with open(error_log_path, "a", encoding="utf-8") as f:
            f.write("\n" + "="*50 + "\n")
            f.write(f"EXCEPTION OCCURRED: {exc_type.__name__}: {exc_value}\n")
            traceback.print_exception(exc_type, exc_value, exc_traceback, file=f)
    except Exception:
        pass
    sys.__excepthook__(exc_type, exc_value, exc_traceback)

sys.excepthook = log_exception

# Placeholders for deferred imports (loaded after splash shows)
pickle = None
multiprocessing = None
re = None
threading = None
np = None
trimesh = None
pv = None
QtInteractor = None

# Quickly import PyQt6 (installed dynamically if missing)
try:
    from PyQt6 import QtWidgets, QtCore, QtGui
except ImportError:
    print("Installing PyQt6 library for graphical user interface...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "PyQt6"])
    from PyQt6 import QtWidgets, QtCore, QtGui

class BeautifulSplashScreen(QtWidgets.QSplashScreen):
    def __init__(self):
        # Create a beautiful dark cyberpixmap
        pixmap = QtGui.QPixmap(480, 280)
        pixmap.fill(QtGui.QColor("#1e272e"))
        super().__init__(pixmap)
        
        # Draw design outline on the pixmap to make it look premium
        painter = QtGui.QPainter(pixmap)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        
        # Border
        pen = QtGui.QPen(QtGui.QColor("#00d2d3"), 3)
        painter.setPen(pen)
        painter.drawRect(1, 1, 478, 278)
        
        # Glowing accent line
        pen2 = QtGui.QPen(QtGui.QColor("#ff007f"), 2)
        painter.setPen(pen2)
        painter.drawLine(10, 220, 470, 220)
        painter.end()
        
        # Re-set updated pixmap
        self.setPixmap(pixmap)
        
        # Custom layout inside the splash screen
        self.frame = QtWidgets.QFrame(self)
        self.frame.setGeometry(0, 0, 480, 280)
        self.frame.setStyleSheet("background: transparent;")
        
        layout = QtWidgets.QVBoxLayout(self.frame)
        layout.setContentsMargins(30, 30, 30, 20)
        
        title_lbl = QtWidgets.QLabel("AI 3D MODEL DESIGNER")
        title_lbl.setStyleSheet("font-size: 22px; font-weight: bold; color: #00d2d3; font-family: 'Segoe UI', sans-serif; background: transparent;")
        title_lbl.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_lbl)
        
        subtitle_lbl = QtWidgets.QLabel("INTELLIGENT CAD FABRICATION SYSTEM")
        subtitle_lbl.setStyleSheet("font-size: 10px; font-weight: 600; color: #ff007f; letter-spacing: 2px; font-family: 'Segoe UI', sans-serif; background: transparent;")
        subtitle_lbl.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle_lbl)
        
        layout.addStretch()
        
        # Status message
        self.status_lbl = QtWidgets.QLabel("Initializing modules...")
        self.status_lbl.setStyleSheet("font-size: 11px; color: #ecf0f1; font-family: monospace; background: transparent;")
        self.status_lbl.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_lbl)
        
        # Progress Bar
        self.progress_bar = QtWidgets.QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(10)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(6)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #2c3e50;
                border-radius: 3px;
                background-color: #2c3e50;
            }
            QProgressBar::chunk {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #ff007f, stop:1 #00d2d3);
                border-radius: 2px;
            }
        """)
        layout.addWidget(self.progress_bar)
        
        # Apply frameless window and keep it on top
        self.setWindowFlags(QtCore.Qt.WindowType.WindowStaysOnTopHint | QtCore.Qt.WindowType.FramelessWindowHint)
        
    def update_status(self, text, val):
        self.status_lbl.setText(text)
        self.progress_bar.setValue(val)
        QtWidgets.QApplication.processEvents()

def check_and_install_dependencies(splash_callback=None):
    """Checks for required libraries and installs them if missing before importing them."""
    if getattr(sys, 'frozen', False):
        return

    # Critical packages (app will fail if these are missing)
    critical = {
        "numpy": "numpy",
        "scipy": "scipy",
        "trimesh": "trimesh",
        "pyvista": "pyvista",
        "pyvistaqt": "pyvistaqt",
        "PyQt6": "PyQt6",
    }
    
    for module, package in critical.items():
        try:
            if importlib.util.find_spec(module) is None:
                raise ImportError
        except (ImportError, ModuleNotFoundError):
            if splash_callback:
                splash_callback(f"Installing critical dependency: {package}...")
            else:
                print(f"Installing critical dependency: {package}...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            except Exception as e:
                print(f"Warning: Failed to install critical dependency {package}: {e}")

# PyInstaller Compatibility Hints
try:
    import scipy.special._cdflib
    import pycparser.lextab
    import pycparser.yacctab
except ImportError:
    pass

# Try to import google-generativeai for PyInstaller detection
try:
    import google.generativeai as genai
except ImportError:
    pass

import json
import re
import traceback

class GeminiSynthesisThread(QtCore.QThread):
    def __init__(self, prompt, parent=None):
        super().__init__(parent)
        self.prompt = prompt
        self.parent_obj = parent

    def run(self):
        # 1. Check API Key
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            self.parent_obj.synthesis_offline.emit(self.prompt)
            return

        self.parent_obj.synthesis_status.emit("Thinking... 🧠", "magenta")
        self.parent_obj.synthesis_log.emit("<b>AI:</b> Contacting Google Gemini for shape synthesis...")

        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
        except ImportError:
            # Install dynamically
            self.parent_obj.synthesis_status.emit("Installing package... 📦", "#feca57")
            self.parent_obj.synthesis_log.emit("<b>AI:</b> Installing required dependency google-generativeai...")
            try:
                import subprocess
                import sys
                subprocess.check_call([sys.executable, "-m", "pip", "install", "google-generativeai"])
                import google.generativeai as genai
                genai.configure(api_key=api_key)
            except Exception as e:
                self.parent_obj.synthesis_error.emit(self.prompt, f"Failed to import/install google-generativeai: {e}", "")
                return

        system_instruction = (
            "You are a professional 3D CAD modeling scriptwriter that generates trimesh python scripts.\n"
            "Generate ONLY valid Python code containing trimesh geometry generation. Do not include any explanations, imports, markdown wrappers except the ```python ``` block.\n"
            "Rules:\n"
            "1. You must construct a single watertight trimesh.Trimesh or trimesh.parent.Geometry object and assign it to the variable named `mesh`.\n"
            "2. Do not use complex boolean operations (union/difference/intersection) unless absolutely necessary, as they frequently fail if meshes are not perfectly manifold. Instead, prefer concatenating meshes using `trimesh.util.concatenate([mesh1, mesh2, ...])`.\n"
            "3. You have pre-imported `trimesh` and `numpy as np`. Do not import them again.\n"
            "4. Keep the design complex, structured, and visually interesting matching the user's description (e.g. humanoid with multiple segments, complex structure, limbs, weapons, pose, wings, etc.). Assemble multiple primitive shapes (spheres, boxes, cylinders, cones) using rotation and translation transformations.\n"
            "5. To rotate or translate components, use `mesh.apply_transform(trimesh.transformations.rotation_matrix(angle_in_radians, axis_vector))` or `mesh.apply_translation(translation_vector)`.\n"
            "6. Make sure there are no syntax errors or undefined variables.\n"
            "7. The final result must be assigned to the variable `mesh`.\n\n"
            "Example code to create a dumbbell:\n"
            "```python\n"
            "bar = trimesh.creation.cylinder(radius=1.5, height=30)\n"
            "bar.apply_translation([0, 0, 15])\n"
            "left_weight = trimesh.creation.cylinder(radius=8, height=4)\n"
            "left_weight.apply_translation([0, 0, 2])\n"
            "right_weight = trimesh.creation.cylinder(radius=8, height=4)\n"
            "right_weight.apply_translation([0, 0, 28])\n"
            "mesh = trimesh.util.concatenate([bar, left_weight, right_weight])\n"
            "```"
        )

        model_name = "gemini-2.0-flash"  # Default model
        
        try:
            model = genai.GenerativeModel(
                model_name=model_name,
                system_instruction=system_instruction
            )
        except Exception as e:
            self.parent_obj.synthesis_error.emit(self.prompt, f"Failed to initialize Gemini Model: {e}", "")
            return

        chat = model.start_chat()
        current_prompt = f"Write a python script to generate a 3D model for: '{self.prompt}'."
        
        code = ""
        max_attempts = 3
        attempt = 0
        
        while attempt < max_attempts:
            attempt += 1
            self.parent_obj.synthesis_status.emit(f"Synthesizing (Try {attempt}/{max_attempts})... 🛠️", "cyan")
            try:
                response = chat.send_message(current_prompt)
                response_text = response.text
                
                code_match = re.search(r"```python\n(.*?)```", response_text, re.DOTALL)
                if not code_match:
                    code_match = re.search(r"```\n(.*?)```", response_text, re.DOTALL)
                
                code = code_match.group(1) if code_match else response_text
                lines = code.split("\n")
                filtered_lines = []
                for line in lines:
                    if line.strip().startswith("import trimesh") or line.strip().startswith("import numpy"):
                        continue
                    filtered_lines.append(line)
                code = "\n".join(filtered_lines)
                
                self.parent_obj.synthesis_log.emit(f"<b>System:</b> Compiling synthesized CAD macro...")
                local_vars = {'trimesh': trimesh, 'np': np, 'mesh': None}
                
                exec(code, {}, local_vars)
                
                generated_mesh = local_vars.get('mesh')
                if generated_mesh is None:
                    raise ValueError("Variable `mesh` was not defined or is None after executing script.")
                
                self.parent_obj.synthesis_status.emit("CAD Core Online!", "#39ff14")
                self.parent_obj.synthesis_success.emit(self.prompt, generated_mesh, code)
                return
                
            except Exception as ex:
                err_type, err_val, err_tb = sys.exc_info()
                tb_lines = traceback.format_exception(err_type, err_val, err_tb)
                tb_str = "".join(tb_lines)
                self.parent_obj.synthesis_log.emit(f"<span style='color: #ff4757;'><b>Error during execution:</b> {ex}</span>")
                
                if attempt == max_attempts:
                    self.parent_obj.synthesis_status.emit("Error! ❌", "#ff4757")
                    self.parent_obj.synthesis_error.emit(self.prompt, f"Failed after {max_attempts} attempts. Last error: {ex}", code)
                    return
                
                current_prompt = (
                    f"The script you generated encountered an error during execution:\n"
                    f"```\n{tb_str}\n```\n"
                    f"Please correct the code. Ensure that you fix the error and assign the output mesh to the `mesh` variable. "
                    f"Return ONLY the corrected Python script inside a ```python ``` block."
                )

class AI3DModeler(QtWidgets.QMainWindow):
    synthesis_success = QtCore.pyqtSignal(str, object, str)
    synthesis_error = QtCore.pyqtSignal(str, str, str)
    synthesis_status = QtCore.pyqtSignal(str, str)
    synthesis_log = QtCore.pyqtSignal(str)
    synthesis_offline = QtCore.pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("AI-Assisted 3D Builder (3MF Support)")
        self.resize(1200, 900)
        self.status_bar = self.statusBar()
        self.current_aesthetic_style = "default"
        self.apply_cyberpunk_theme()
        
        # Flashforge AD5X Constants (mm)
        self.BUILD_LIMITS = [220, 220, 220] 
        self.UNIT = "mm"

        # State management for meshes and UI
        self.meshes = {}  # Dictionary to store trimesh objects: {name: trimesh_obj}
        self.selected_mesh_name = None
        self.current_colors = [QtGui.QColor("white"), QtGui.QColor("cyan")]
        self.density_level = 1  # Default subdivision level
        self.last_duplicate_offset = np.array([15, 15, 0]) # For Smart Duplication
        self.active_selection_indices = None # For targeted texturing
        self.pattern_functions = {} # Registry for texture functions
        self.is_listening = False
        self.grid_resolution = 25  # Default grid resolution for marching cubes
        self.ai_chat_history = []
        self.custom_macros = {}
        self.last_executed_code = None

        self.undo_stack = [] # History for "Rock Solid" Undo support
        self.redo_stack = []
        self.init_pattern_registry()
        self.load_macros()

        # Connect AI synthesis thread signals
        self.synthesis_success.connect(self._handle_synthesis_success)
        self.synthesis_error.connect(self._handle_synthesis_error)
        self.synthesis_status.connect(self.set_ai_status)
        self.synthesis_log.connect(self._log_ai_chat)
        self.synthesis_offline.connect(self._handle_offline_fallback)

        # Main Layout Setup
        self.central_widget = QtWidgets.QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_h_layout = QtWidgets.QHBoxLayout(self.central_widget)
        
        self.layout = QtWidgets.QVBoxLayout()
        self.main_h_layout.addLayout(self.layout, stretch=4)

        # 1. Design Section (3D Canvas)
        # PyVista provides the high-detail rendering and zoom/pan/rotate capabilities
        self.plotter = QtInteractor(self.central_widget)
        self.layout.addWidget(self.plotter.interactor, stretch=5)
        self.plotter.add_axes()
        self.plotter.view_isometric()
        self.plotter.set_background("gray") # Professional builder aesthetic
        # Initialize UI Components
        self.init_toolbar()
        self.init_ai_section()
        # Visuals: Add Flashforge AD5X Build Plate
        self.draw_build_plate()

        # Ensure interaction mode is clean on startup
        self.plotter.disable_picking()
        self.plotter.enable_mesh_picking(callback=self.on_mesh_picked, show=False)
        self.plotter.iren.add_observer("KeyPressEvent", self._on_key_press)

        # NEW: Direct Drag Support via Shift + Left Click
        self.is_dragging = False
        self.snap_to_grid = True # Professional precision default
        self.drag_start_world = None
        self.plotter.iren.add_observer("LeftButtonPressEvent", self._on_drag_start)
        self.plotter.iren.add_observer("MouseMoveEvent", self._on_drag_move)
        self.plotter.iren.add_observer("LeftButtonReleaseEvent", self._on_drag_end)

        # 2. Scene Management, Creative Mode & Art Palette (Right Sidebar using Tabs)
        self.sidebar_tabs = QtWidgets.QTabWidget()
        self.main_h_layout.addWidget(self.sidebar_tabs, stretch=1)
        
        # Tab 1: Parts Manager (Scene)
        self.scene_tab = QtWidgets.QWidget()
        self.scene_tab_layout = QtWidgets.QVBoxLayout(self.scene_tab)
        self.right_sidebar = self.scene_tab_layout
        self.init_scene_tree()
        self.sidebar_tabs.addTab(self.scene_tab, "Parts Manager")
        
        # Tab 2: Creative Mode
        self.creative_tab = QtWidgets.QWidget()
        self.creative_tab_layout = QtWidgets.QVBoxLayout(self.creative_tab)
        self.right_sidebar = self.creative_tab_layout
        self.init_creative_mode_panel()
        self.sidebar_tabs.addTab(self.creative_tab, "Creative Mode")
        
        # Tab 3: Art Palette
        self.art_tab = QtWidgets.QWidget()
        self.art_tab_layout = QtWidgets.QVBoxLayout(self.art_tab)
        self.right_sidebar = self.art_tab_layout
        self.init_art_palette()
        self.sidebar_tabs.addTab(self.art_tab, "Art & Textures")
        
        # Tab 4: AI Macros
        self.macro_tab = QtWidgets.QWidget()
        self.macro_tab_layout = QtWidgets.QVBoxLayout(self.macro_tab)
        self.init_macro_panel()
        self.sidebar_tabs.addTab(self.macro_tab, "AI Macros")

    def init_scene_tree(self):
        """Creates a list of all objects in the scene for easy selection."""
        scene_group = QtWidgets.QGroupBox("Parts Manager (Scene Tree)")
        scene_layout = QtWidgets.QVBoxLayout()

        self.object_list = QtWidgets.QListWidget()
        self.object_list.setToolTip("Right-click a part to remove or rename it independently")
        self.object_list.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.ExtendedSelection)
        self.object_list.itemClicked.connect(self.select_from_list)
        
        # Enable independent management via right-click context menu
        self.object_list.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)
        self.object_list.customContextMenuRequested.connect(self.show_context_menu)
        
        scene_layout.addWidget(self.object_list)

        # Quick Actions
        rename_btn = QtWidgets.QPushButton("✎ Rename Selected")
        rename_btn.clicked.connect(self.rename_selected)
        scene_layout.addWidget(rename_btn)

        # Tabs for transforms: Move, Rotate, Scale
        self.transform_tabs = QtWidgets.QTabWidget()
        
        # Tab 1: Move
        move_widget = QtWidgets.QWidget()
        move_layout = QtWidgets.QVBoxLayout(move_widget)
        move_grid = QtWidgets.QGridLayout()
        self.pos_x = QtWidgets.QDoubleSpinBox(); self.pos_x.setRange(-200, 200); self.pos_x.setSingleStep(1.0)
        self.pos_y = QtWidgets.QDoubleSpinBox(); self.pos_y.setRange(-200, 200); self.pos_y.setSingleStep(1.0)
        self.pos_z = QtWidgets.QDoubleSpinBox(); self.pos_z.setRange(-200, 500); self.pos_z.setSingleStep(1.0)
        move_grid.addWidget(QtWidgets.QLabel("X Centroid:"), 0, 0); move_grid.addWidget(self.pos_x, 0, 1)
        move_grid.addWidget(QtWidgets.QLabel("Y Centroid:"), 1, 0); move_grid.addWidget(self.pos_y, 1, 1)
        move_grid.addWidget(QtWidgets.QLabel("Z Centroid:"), 2, 0); move_grid.addWidget(self.pos_z, 2, 1)
        apply_move_btn = QtWidgets.QPushButton("Apply Move")
        apply_move_btn.clicked.connect(self.manual_move)
        move_layout.addLayout(move_grid)
        move_layout.addWidget(apply_move_btn)
        self.transform_tabs.addTab(move_widget, "Move")
        
        # Tab 2: Rotate
        rot_widget = QtWidgets.QWidget()
        rot_layout = QtWidgets.QVBoxLayout(rot_widget)
        rot_grid = QtWidgets.QGridLayout()
        self.rot_x = QtWidgets.QDoubleSpinBox(); self.rot_x.setRange(-360, 360); self.rot_x.setValue(0.0); self.rot_x.setSingleStep(5.0)
        self.rot_y = QtWidgets.QDoubleSpinBox(); self.rot_y.setRange(-360, 360); self.rot_y.setValue(0.0); self.rot_y.setSingleStep(5.0)
        self.rot_z = QtWidgets.QDoubleSpinBox(); self.rot_z.setRange(-360, 360); self.rot_z.setValue(0.0); self.rot_z.setSingleStep(5.0)
        rot_grid.addWidget(QtWidgets.QLabel("X Angle (°):"), 0, 0); rot_grid.addWidget(self.rot_x, 0, 1)
        rot_grid.addWidget(QtWidgets.QLabel("Y Angle (°):"), 1, 0); rot_grid.addWidget(self.rot_y, 1, 1)
        rot_grid.addWidget(QtWidgets.QLabel("Z Angle (°):"), 2, 0); rot_grid.addWidget(self.rot_z, 2, 1)
        apply_rot_btn = QtWidgets.QPushButton("Apply Rotation")
        apply_rot_btn.clicked.connect(self.manual_rotate)
        rot_layout.addLayout(rot_grid)
        rot_layout.addWidget(apply_rot_btn)
        self.transform_tabs.addTab(rot_widget, "Rotate")
        
        # Tab 3: Scale
        scale_widget = QtWidgets.QWidget()
        scale_layout = QtWidgets.QVBoxLayout(scale_widget)
        scale_grid = QtWidgets.QGridLayout()
        self.scale_x = QtWidgets.QDoubleSpinBox(); self.scale_x.setRange(0.01, 100); self.scale_x.setValue(1.0); self.scale_x.setSingleStep(0.1)
        self.scale_y = QtWidgets.QDoubleSpinBox(); self.scale_y.setRange(0.01, 100); self.scale_y.setValue(1.0); self.scale_y.setSingleStep(0.1)
        self.scale_z = QtWidgets.QDoubleSpinBox(); self.scale_z.setRange(0.01, 100); self.scale_z.setValue(1.0); self.scale_z.setSingleStep(0.1)
        
        self.uniform_scale_cb = QtWidgets.QCheckBox("Uniform Scaling")
        self.uniform_scale_cb.setChecked(True)
        
        def on_scale_x_changed(val):
            if self.uniform_scale_cb.isChecked():
                self.scale_y.blockSignals(True)
                self.scale_z.blockSignals(True)
                self.scale_y.setValue(val)
                self.scale_z.setValue(val)
                self.scale_y.blockSignals(False)
                self.scale_z.blockSignals(False)
                
        def on_scale_y_changed(val):
            if self.uniform_scale_cb.isChecked():
                self.scale_x.blockSignals(True)
                self.scale_z.blockSignals(True)
                self.scale_x.setValue(val)
                self.scale_z.setValue(val)
                self.scale_x.blockSignals(False)
                self.scale_z.blockSignals(False)
                
        def on_scale_z_changed(val):
            if self.uniform_scale_cb.isChecked():
                self.scale_x.blockSignals(True)
                self.scale_y.blockSignals(True)
                self.scale_x.setValue(val)
                self.scale_y.setValue(val)
                self.scale_x.blockSignals(False)
                self.scale_y.blockSignals(False)
                
        self.scale_x.valueChanged.connect(on_scale_x_changed)
        self.scale_y.valueChanged.connect(on_scale_y_changed)
        self.scale_z.valueChanged.connect(on_scale_z_changed)
        
        scale_grid.addWidget(QtWidgets.QLabel("Scale X:"), 0, 0); scale_grid.addWidget(self.scale_x, 0, 1)
        scale_grid.addWidget(QtWidgets.QLabel("Scale Y:"), 1, 0); scale_grid.addWidget(self.scale_y, 1, 1)
        scale_grid.addWidget(QtWidgets.QLabel("Scale Z:"), 2, 0); scale_grid.addWidget(self.scale_z, 2, 1)
        apply_scale_btn = QtWidgets.QPushButton("Apply Scale")
        apply_scale_btn.clicked.connect(self.manual_scale)
        scale_layout.addLayout(scale_grid)
        scale_layout.addWidget(self.uniform_scale_cb)
        scale_layout.addWidget(apply_scale_btn)
        self.transform_tabs.addTab(scale_widget, "Scale")
        
        scene_layout.addWidget(self.transform_tabs)
        
        drop_bed_btn = QtWidgets.QPushButton("📐 Drop Selected to Bed")
        drop_bed_btn.clicked.connect(self.drop_to_bed_selected)
        scene_layout.addWidget(drop_bed_btn)

        delete_btn = QtWidgets.QPushButton("🗑 Delete Selected")
        delete_btn.setStyleSheet("color: red;")
        delete_btn.clicked.connect(self.delete_selected)
        scene_layout.addWidget(delete_btn)

        scene_group.setLayout(scene_layout)
        self.right_sidebar.addWidget(scene_group)

    def init_creative_mode_panel(self):
        """Creates the Creative Mode design panel with real-time sliders and advanced modifiers."""
        creative_group = QtWidgets.QGroupBox("Creative Editor")
        layout = QtWidgets.QVBoxLayout(creative_group)
        
        # Enable Creative Mode Checkbox
        self.creative_mode_active = QtWidgets.QCheckBox("🔓 Enable Creative Mode")
        self.creative_mode_active.setStyleSheet("font-weight: bold; color: #00d2d3; font-size: 11px;")
        self.creative_mode_active.setToolTip("Unlocks real-time resizing sliders, organic reshaping deformers, and advanced geometry tools.")
        self.creative_mode_active.stateChanged.connect(self.toggle_creative_mode)
        layout.addWidget(self.creative_mode_active)
        
        # Scroll Area for sliders and tools
        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QtWidgets.QWidget()
        scroll_layout = QtWidgets.QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        
        # Group 1: Real-time Resize & Rotate
        transform_group = QtWidgets.QGroupBox("Real-time Resize & Rotate")
        t_layout = QtWidgets.QVBoxLayout(transform_group)
        
        # Link scale axes
        self.creative_link_axes = QtWidgets.QCheckBox("Lock Axes (Uniform Scale)")
        self.creative_link_axes.setChecked(True)
        t_layout.addWidget(self.creative_link_axes)
        
        # Scale Sliders
        t_layout.addWidget(QtWidgets.QLabel("Scale X (Width)"))
        self.creative_scale_x = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        self.creative_scale_x.setRange(10, 300) # 0.1x to 3.0x
        self.creative_scale_x.setValue(100) # 1.0x
        self.creative_scale_x.sliderPressed.connect(self.on_slider_pressed)
        self.creative_scale_x.valueChanged.connect(self.apply_creative_transforms)
        self.creative_scale_x.sliderReleased.connect(self.on_slider_released)
        t_layout.addWidget(self.creative_scale_x)
        
        t_layout.addWidget(QtWidgets.QLabel("Scale Y (Depth)"))
        self.creative_scale_y = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        self.creative_scale_y.setRange(10, 300)
        self.creative_scale_y.setValue(100)
        self.creative_scale_y.sliderPressed.connect(self.on_slider_pressed)
        self.creative_scale_y.valueChanged.connect(self.apply_creative_transforms)
        self.creative_scale_y.sliderReleased.connect(self.on_slider_released)
        t_layout.addWidget(self.creative_scale_y)
        
        t_layout.addWidget(QtWidgets.QLabel("Scale Z (Height)"))
        self.creative_scale_z = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        self.creative_scale_z.setRange(10, 300)
        self.creative_scale_z.setValue(100)
        self.creative_scale_z.sliderPressed.connect(self.on_slider_pressed)
        self.creative_scale_z.valueChanged.connect(self.apply_creative_transforms)
        self.creative_scale_z.sliderReleased.connect(self.on_slider_released)
        t_layout.addWidget(self.creative_scale_z)
        
        # Sync uniform sliders
        self.creative_scale_x.valueChanged.connect(self.on_scale_slider_changed)
        self.creative_scale_y.valueChanged.connect(self.on_scale_slider_changed)
        self.creative_scale_z.valueChanged.connect(self.on_scale_slider_changed)
        
        # Rotation Sliders
        t_layout.addWidget(QtWidgets.QLabel("Rotate X (Pitch)"))
        self.creative_rot_x = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        self.creative_rot_x.setRange(-180, 180)
        self.creative_rot_x.setValue(0)
        self.creative_rot_x.sliderPressed.connect(self.on_slider_pressed)
        self.creative_rot_x.valueChanged.connect(self.apply_creative_transforms)
        self.creative_rot_x.sliderReleased.connect(self.on_slider_released)
        t_layout.addWidget(self.creative_rot_x)
        
        t_layout.addWidget(QtWidgets.QLabel("Rotate Y (Roll)"))
        self.creative_rot_y = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        self.creative_rot_y.setRange(-180, 180)
        self.creative_rot_y.setValue(0)
        self.creative_rot_y.sliderPressed.connect(self.on_slider_pressed)
        self.creative_rot_y.valueChanged.connect(self.apply_creative_transforms)
        self.creative_rot_y.sliderReleased.connect(self.on_slider_released)
        t_layout.addWidget(self.creative_rot_y)
        
        t_layout.addWidget(QtWidgets.QLabel("Rotate Z (Yaw)"))
        self.creative_rot_z = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        self.creative_rot_z.setRange(-180, 180)
        self.creative_rot_z.setValue(0)
        self.creative_rot_z.sliderPressed.connect(self.on_slider_pressed)
        self.creative_rot_z.valueChanged.connect(self.apply_creative_transforms)
        self.creative_rot_z.sliderReleased.connect(self.on_slider_released)
        t_layout.addWidget(self.creative_rot_z)
        
        scroll_layout.addWidget(transform_group)
        
        # Group 2: Mesh Deformers (Reshape)
        deform_group = QtWidgets.QGroupBox("Mesh Deformers (Reshape)")
        d_layout = QtWidgets.QVBoxLayout(deform_group)
        
        d_layout.addWidget(QtWidgets.QLabel("Twist Angle"))
        self.creative_twist = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        self.creative_twist.setRange(-360, 360)
        self.creative_twist.setValue(0)
        self.creative_twist.sliderPressed.connect(self.on_slider_pressed)
        self.creative_twist.valueChanged.connect(self.apply_creative_deforms)
        self.creative_twist.sliderReleased.connect(self.on_slider_released)
        d_layout.addWidget(self.creative_twist)
        
        d_layout.addWidget(QtWidgets.QLabel("Taper Ratio"))
        self.creative_taper = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        self.creative_taper.setRange(10, 300) # 0.1 to 3.0
        self.creative_taper.setValue(100) # 1.0
        self.creative_taper.sliderPressed.connect(self.on_slider_pressed)
        self.creative_taper.valueChanged.connect(self.apply_creative_deforms)
        self.creative_taper.sliderReleased.connect(self.on_slider_released)
        d_layout.addWidget(self.creative_taper)
        
        d_layout.addWidget(QtWidgets.QLabel("Bend Angle"))
        self.creative_bend = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        self.creative_bend.setRange(-180, 180)
        self.creative_bend.setValue(0)
        self.creative_bend.sliderPressed.connect(self.on_slider_pressed)
        self.creative_bend.valueChanged.connect(self.apply_creative_deforms)
        self.creative_bend.sliderReleased.connect(self.on_slider_released)
        d_layout.addWidget(self.creative_bend)
        
        d_layout.addWidget(QtWidgets.QLabel("Bulge / Swell"))
        self.creative_bulge = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        self.creative_bulge.setRange(-200, 200) # -2.0 to 2.0
        self.creative_bulge.setValue(0)
        self.creative_bulge.sliderPressed.connect(self.on_slider_pressed)
        self.creative_bulge.valueChanged.connect(self.apply_creative_deforms)
        self.creative_bulge.sliderReleased.connect(self.on_slider_released)
        d_layout.addWidget(self.creative_bulge)
        
        d_layout.addWidget(QtWidgets.QLabel("Organic Noise (Ruffles)"))
        self.creative_noise = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        self.creative_noise.setRange(0, 100) # 0 to 10.0mm
        self.creative_noise.setValue(0)
        self.creative_noise.sliderPressed.connect(self.on_slider_pressed)
        self.creative_noise.valueChanged.connect(self.apply_creative_deforms)
        self.creative_noise.sliderReleased.connect(self.on_slider_released)
        d_layout.addWidget(self.creative_noise)
        
        d_layout.addWidget(QtWidgets.QLabel("Laplacian Smoothing"))
        self.creative_smooth = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        self.creative_smooth.setRange(0, 50)
        self.creative_smooth.setValue(0)
        self.creative_smooth.sliderPressed.connect(self.on_slider_pressed)
        self.creative_smooth.valueChanged.connect(self.apply_creative_deforms)
        self.creative_smooth.sliderReleased.connect(self.on_slider_released)
        d_layout.addWidget(self.creative_smooth)
        
        scroll_layout.addWidget(deform_group)
        
        # Group 3: Creative Modifiers & Tools
        mods_group = QtWidgets.QGroupBox("Creative Geometry Modifiers")
        m_layout = QtWidgets.QVBoxLayout(mods_group)
        
        # Voxelizer controls
        m_layout.addWidget(QtWidgets.QLabel("Voxel Grid Size (mm)"))
        self.voxel_pitch_slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        self.voxel_pitch_slider.setRange(2, 20)
        self.voxel_pitch_slider.setValue(5)
        m_layout.addWidget(self.voxel_pitch_slider)
        
        self.btn_voxelize = QtWidgets.QPushButton("👾 Voxelize Mesh")
        self.btn_voxelize.clicked.connect(self.creative_voxelize)
        m_layout.addWidget(self.btn_voxelize)
        
        # Decimation controls
        m_layout.addWidget(QtWidgets.QLabel("Low-Poly Decimate Ratio"))
        self.decimate_slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        self.decimate_slider.setRange(10, 90) # 10% to 90%
        self.decimate_slider.setValue(50)
        m_layout.addWidget(self.decimate_slider)
        
        self.btn_decimate = QtWidgets.QPushButton("📉 Decimate Shape")
        self.btn_decimate.clicked.connect(self.creative_decimate)
        m_layout.addWidget(self.btn_decimate)
        
        # Subdivision and shelling
        self.btn_subdivide = QtWidgets.QPushButton("📈 Subdivide (Add Res)")
        self.btn_subdivide.clicked.connect(self.creative_subdivide)
        m_layout.addWidget(self.btn_subdivide)
        
        m_layout.addWidget(QtWidgets.QLabel("Shell Wall Thickness (mm)"))
        self.shell_thickness_slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        self.shell_thickness_slider.setRange(1, 10)
        self.shell_thickness_slider.setValue(2)
        m_layout.addWidget(self.shell_thickness_slider)
        
        self.btn_shell = QtWidgets.QPushButton("🐚 Hollow Out (Shell)")
        self.btn_shell.clicked.connect(self.creative_shell)
        m_layout.addWidget(self.btn_shell)
        
        # Boolean buttons
        m_layout.addWidget(QtWidgets.QLabel("Solid CSG Booleans (Select 2+ Parts)"))
        bool_layout = QtWidgets.QHBoxLayout()
        self.btn_bool_union = QtWidgets.QPushButton("Union")
        self.btn_bool_union.clicked.connect(lambda: self.run_boolean("union"))
        self.btn_bool_diff = QtWidgets.QPushButton("Subtract")
        self.btn_bool_diff.clicked.connect(lambda: self.run_boolean("difference"))
        self.btn_bool_intersect = QtWidgets.QPushButton("Intersect")
        self.btn_bool_intersect.clicked.connect(lambda: self.run_boolean("intersection"))
        
        bool_layout.addWidget(self.btn_bool_union)
        bool_layout.addWidget(self.btn_bool_diff)
        bool_layout.addWidget(self.btn_bool_intersect)
        m_layout.addLayout(bool_layout)
        
        # Quick actions
        m_layout.addWidget(QtWidgets.QLabel("Quick Alignments"))
        align_layout = QtWidgets.QHBoxLayout()
        btn_center = QtWidgets.QPushButton("Center Selected")
        btn_center.clicked.connect(self.creative_center_selected)
        btn_drop = QtWidgets.QPushButton("Drop to Bed")
        btn_drop.clicked.connect(self.drop_to_bed_selected)
        align_layout.addWidget(btn_center)
        align_layout.addWidget(btn_drop)
        m_layout.addLayout(align_layout)
        
        scroll_layout.addWidget(mods_group)
        
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)
        
        # Set layout
        creative_group.setLayout(layout)
        self.right_sidebar.addWidget(creative_group)
        
        # Initially trigger toggle to disabled state
        self.toggle_creative_mode(False)

    def toggle_creative_mode(self, enabled):
        """Enables or disables Creative Mode inputs and shows help feedback."""
        self.creative_scale_x.setEnabled(enabled)
        self.creative_scale_y.setEnabled(enabled)
        self.creative_scale_z.setEnabled(enabled)
        self.creative_rot_x.setEnabled(enabled)
        self.creative_rot_y.setEnabled(enabled)
        self.creative_rot_z.setEnabled(enabled)
        self.creative_twist.setEnabled(enabled)
        self.creative_taper.setEnabled(enabled)
        self.creative_bend.setEnabled(enabled)
        self.creative_bulge.setEnabled(enabled)
        self.creative_noise.setEnabled(enabled)
        self.creative_smooth.setEnabled(enabled)
        
        self.voxel_pitch_slider.setEnabled(enabled)
        self.btn_voxelize.setEnabled(enabled)
        self.decimate_slider.setEnabled(enabled)
        self.btn_decimate.setEnabled(enabled)
        self.btn_subdivide.setEnabled(enabled)
        self.shell_thickness_slider.setEnabled(enabled)
        self.btn_shell.setEnabled(enabled)
        self.btn_bool_union.setEnabled(enabled)
        self.btn_bool_diff.setEnabled(enabled)
        self.btn_bool_intersect.setEnabled(enabled)
        
        if enabled:
            self.chat_history.append("<b>Creative Mode Activated!</b> Real-time sliders, CSG booleans, and reshaping deformers are unlocked. Select any part to begin editing.")
            self.creative_mode_active.setText("🔓 Creative Mode Active")
        else:
            self.creative_mode_active.setText("🔒 Enable Creative Mode")

    def reset_creative_sliders(self):
        """Resets the sliders in the Creative Mode panel to their default neutral values without triggering updates."""
        if not hasattr(self, 'creative_scale_x'): return
        
        self.creative_scale_x.blockSignals(True)
        self.creative_scale_y.blockSignals(True)
        self.creative_scale_z.blockSignals(True)
        self.creative_rot_x.blockSignals(True)
        self.creative_rot_y.blockSignals(True)
        self.creative_rot_z.blockSignals(True)
        self.creative_twist.blockSignals(True)
        self.creative_taper.blockSignals(True)
        self.creative_bend.blockSignals(True)
        self.creative_bulge.blockSignals(True)
        self.creative_noise.blockSignals(True)
        self.creative_smooth.blockSignals(True)
        
        self.creative_scale_x.setValue(100) # 1.0 represented as 100
        self.creative_scale_y.setValue(100)
        self.creative_scale_z.setValue(100)
        self.creative_rot_x.setValue(0)
        self.creative_rot_y.setValue(0)
        self.creative_rot_z.setValue(0)
        self.creative_twist.setValue(0)
        self.creative_taper.setValue(100) # 1.0 represented as 100
        self.creative_bend.setValue(0)
        self.creative_bulge.setValue(0)
        self.creative_noise.setValue(0)
        self.creative_smooth.setValue(0)
        
        self.creative_scale_x.blockSignals(False)
        self.creative_scale_y.blockSignals(False)
        self.creative_scale_z.blockSignals(False)
        self.creative_rot_x.blockSignals(False)
        self.creative_rot_y.blockSignals(False)
        self.creative_rot_z.blockSignals(False)
        self.creative_twist.blockSignals(False)
        self.creative_taper.blockSignals(False)
        self.creative_bend.blockSignals(False)
        self.creative_bulge.blockSignals(False)
        self.creative_noise.blockSignals(False)
        self.creative_smooth.blockSignals(False)

    def on_slider_pressed(self):
        """Captures the starting geometry state of the selected mesh when a transform slider begins dragging."""
        if self.selected_mesh_name and self.selected_mesh_name in self.meshes:
            self.creative_start_mesh = self.meshes[self.selected_mesh_name].copy()

    def on_slider_released(self):
        """Commits the relative slider adjustments and registers the state in the undo history."""
        self.save_state()
        self.reset_creative_sliders()
        self.creative_start_mesh = None
        self.chat_history.append(f"<b>System:</b> Creative transformation committed for '{self.selected_mesh_name}'.")

    def on_scale_slider_changed(self, value):
        """Enforces uniform scaling across all three coordinate axes if the lock is active."""
        if not hasattr(self, 'creative_link_axes') or not self.creative_link_axes.isChecked():
            return
        self.creative_scale_x.blockSignals(True)
        self.creative_scale_y.blockSignals(True)
        self.creative_scale_z.blockSignals(True)
        
        self.creative_scale_x.setValue(value)
        self.creative_scale_y.setValue(value)
        self.creative_scale_z.setValue(value)
        
        self.creative_scale_x.blockSignals(False)
        self.creative_scale_y.blockSignals(False)
        self.creative_scale_z.blockSignals(False)

    def apply_creative_transforms(self):
        """Applies real-time scaling and rotation transformations to the captured starting geometry state."""
        if not self.selected_mesh_name or self.selected_mesh_name not in self.meshes:
            return
            
        if not hasattr(self, 'creative_start_mesh') or self.creative_start_mesh is None:
            self.creative_start_mesh = self.meshes[self.selected_mesh_name].copy()
            
        sx = self.creative_scale_x.value() / 100.0
        sy = self.creative_scale_y.value() / 100.0
        sz = self.creative_scale_z.value() / 100.0
        
        rx = np.radians(self.creative_rot_x.value())
        ry = np.radians(self.creative_rot_y.value())
        rz = np.radians(self.creative_rot_z.value())
        
        mesh = self.creative_start_mesh.copy()
        cx, cy, cz = mesh.centroid[0], mesh.centroid[1], mesh.centroid[2]
        mesh.apply_translation([-cx, -cy, -cz])
        
        scale_mat = np.diag([sx, sy, sz, 1.0])
        mesh.apply_transform(scale_mat)
        
        if rx != 0:
            rot_x_mat = trimesh.transformations.rotation_matrix(rx, [1, 0, 0])
            mesh.apply_transform(rot_x_mat)
        if ry != 0:
            rot_y_mat = trimesh.transformations.rotation_matrix(ry, [0, 1, 0])
            mesh.apply_transform(rot_y_mat)
        if rz != 0:
            rot_z_mat = trimesh.transformations.rotation_matrix(rz, [0, 0, 1])
            mesh.apply_transform(rot_z_mat)
            
        mesh.apply_translation([cx, cy, cz])
        
        self.meshes[self.selected_mesh_name] = mesh
        self.update_canvas()

    def apply_creative_deforms(self):
        """Applies real-time organic deforms (taper, bend, twist, bulge, noise, smooth) to the starting geometry."""
        if not self.selected_mesh_name or self.selected_mesh_name not in self.meshes:
            self.get_active_mesh()
            
        if not hasattr(self, 'creative_start_mesh') or self.creative_start_mesh is None:
            self.creative_start_mesh = self.meshes[self.selected_mesh_name].copy()
            
        mesh = self.creative_start_mesh.copy()
        
        twist_val = self.creative_twist.value()
        taper_val = self.creative_taper.value() / 100.0
        bend_val = self.creative_bend.value()
        bulge_val = self.creative_bulge.value() / 100.0
        noise_val = self.creative_noise.value() / 10.0
        smooth_val = self.creative_smooth.value()
        
        # 1. Twist
        if twist_val != 0:
            angle_rad = np.radians(twist_val)
            z = mesh.vertices[:, 2]; z_min = z.min(); z_max = z.max()
            if z_max != z_min:
                cx, cy = mesh.centroid[0], mesh.centroid[1]
                x = mesh.vertices[:, 0] - cx
                y = mesh.vertices[:, 1] - cy
                theta = angle_rad * (z - z_min) / (z_max - z_min)
                c, s = np.cos(theta), np.sin(theta)
                mesh.vertices[:, 0] = cx + (x * c - y * s)
                mesh.vertices[:, 1] = cy + (x * s + y * c)
                
        # 2. Taper
        if taper_val != 1.0:
            z = mesh.vertices[:, 2]; z_min, z_max = z.min(), z.max()
            if z_max != z_min:
                cx, cy = mesh.centroid[0], mesh.centroid[1]
                x = mesh.vertices[:, 0] - cx
                y = mesh.vertices[:, 1] - cy
                factor = 1.0 + (taper_val - 1.0) * (z - z_min) / (z_max - z_min)
                mesh.vertices[:, 0] = cx + x * factor
                mesh.vertices[:, 1] = cy + y * factor
                
        # 3. Bend
        if abs(bend_val) > 0.1:
            z = mesh.vertices[:, 2]; z_min, z_max = z.min(), z.max()
            height = z_max - z_min
            if height > 1e-5:
                angle_rad = np.radians(bend_val)
                R = height / angle_rad
                cx = mesh.centroid[0]
                x_rel = mesh.vertices[:, 0] - cx
                theta = (z - z_min) / R
                mesh.vertices[:, 0] = cx + (R + x_rel) * np.cos(theta) - R
                mesh.vertices[:, 2] = z_min + (R + x_rel) * np.sin(theta)
                
        # 4. Bulge
        if abs(bulge_val) > 0.01:
            z = mesh.vertices[:, 2]; z_min, z_max = z.min(), z.max()
            if z_max != z_min:
                height = z_max - z_min
                cx, cy = mesh.centroid[0], mesh.centroid[1]
                x = mesh.vertices[:, 0] - cx
                y = mesh.vertices[:, 1] - cy
                z_norm = (z - z_min) / height
                envelope = np.sin(z_norm * np.pi)
                factor = 1.0 + bulge_val * envelope
                mesh.vertices[:, 0] = cx + x * factor
                mesh.vertices[:, 1] = cy + y * factor
                
        # 5. Organic Noise (Ruffles)
        if noise_val > 0.01:
            normals = mesh.vertex_normals
            x_coords = mesh.vertices[:, 0]
            y_coords = mesh.vertices[:, 1]
            z_coords = mesh.vertices[:, 2]
            
            perturbation = np.sin(x_coords * 0.1) * np.cos(y_coords * 0.1) * np.sin(z_coords * 0.1)
            mesh.vertices += normals * (perturbation[:, np.newaxis] * noise_val)
            
        # 6. Laplacian Smoothing
        if smooth_val > 0:
            trimesh.smoothing.filter_laplacian(mesh, iterations=int(smooth_val))
            
        self.meshes[self.selected_mesh_name] = mesh
        self.update_canvas()

    def creative_voxelize(self):
        """Converts the selected mesh geometry into uniform solid block box voxels."""
        if not self.selected_mesh_name: return
        self.save_state()
        mesh = self.meshes[self.selected_mesh_name]
        pitch = self.voxel_pitch_slider.value()
        try:
            vox = mesh.voxelized(pitch)
            voxel_mesh = vox.as_boxes()
            self.meshes[self.selected_mesh_name] = voxel_mesh
            self.update_canvas()
            self.chat_history.append(f"<b>System:</b> Voxelized '{self.selected_mesh_name}' with voxel size {pitch}mm.")
        except Exception as e:
            self.chat_history.append(f"<b>Error:</b> Failed to voxelize mesh: {e}")

    def creative_subdivide(self):
        """Linearly subdivides the selected mesh to increase geometry density."""
        if not self.selected_mesh_name: return
        self.save_state()
        mesh = self.meshes[self.selected_mesh_name]
        try:
            vertices, faces = trimesh.remesh.subdivide(mesh.vertices, mesh.faces)
            new_mesh = trimesh.Trimesh(vertices=vertices, faces=faces, process=False)
            self.meshes[self.selected_mesh_name] = new_mesh
            self.update_canvas()
            self.chat_history.append(f"<b>System:</b> Subdivided '{self.selected_mesh_name}'. Triangles: {len(new_mesh.faces)}")
        except Exception as e:
            self.chat_history.append(f"<b>Error:</b> Subdivision failed: {e}")

    def creative_decimate(self):
        """Simplifies the mesh geometry using quadric decimation to create a low-poly style."""
        if not self.selected_mesh_name: return
        self.save_state()
        mesh = self.meshes[self.selected_mesh_name]
        ratio = self.decimate_slider.value() / 100.0
        try:
            target_faces = int(len(mesh.faces) * ratio)
            if target_faces < 4:
                self.chat_history.append("<b>Error:</b> Target faces count is too low.")
                return
            decimated_mesh = mesh.simplify_quadric_decimation(target_faces)
            self.meshes[self.selected_mesh_name] = decimated_mesh
            self.update_canvas()
            self.chat_history.append(f"<b>System:</b> Decimated '{self.selected_mesh_name}' by {ratio*100:.0f}% ratio. Triangles: {len(decimated_mesh.faces)}")
        except Exception as e:
            self.chat_history.append(f"<b>Error:</b> Decimation failed: {e}")

    def creative_shell(self):
        """Creates a hollow double-walled shell from the selected solid mesh."""
        if not self.selected_mesh_name: return
        self.save_state()
        mesh = self.meshes[self.selected_mesh_name]
        thickness = self.shell_thickness_slider.value()
        try:
            normals = mesh.vertex_normals
            inner_vertices = mesh.vertices - normals * thickness
            inner_faces = mesh.faces[:, [0, 2, 1]]
            inner_mesh = trimesh.Trimesh(vertices=inner_vertices, faces=inner_faces, process=False)
            shell_mesh = trimesh.util.concatenate([mesh, inner_mesh])
            self.meshes[self.selected_mesh_name] = shell_mesh
            self.update_canvas()
            self.chat_history.append(f"<b>System:</b> Shelled '{self.selected_mesh_name}' with wall thickness {thickness}mm.")
        except Exception as e:
            self.chat_history.append(f"<b>Error:</b> Shelling failed: {e}")

    def run_boolean(self, op_type):
        """Performs CSG boolean logic operations (Union, Subtract, Intersect) on selected parts."""
        selected_items = self.object_list.selectedItems()
        if len(selected_items) < 2:
            QtWidgets.QMessageBox.warning(self, "Selection Required", "Please select at least two shapes in the Parts Manager tree (Ctrl+Click) to perform boolean operations.")
            return
            
        self.save_state()
        try:
            mesh_names = [item.text() for item in selected_items]
            base_name = mesh_names[0]
            base_mesh = self.meshes[base_name]
            other_meshes = [self.meshes[name] for name in mesh_names[1:]]
            
            if op_type == "union":
                result = trimesh.boolean.union([base_mesh] + other_meshes, engine='scad')
            elif op_type == "difference":
                result = trimesh.boolean.difference(base_mesh, trimesh.boolean.union(other_meshes, engine='scad'), engine='scad')
            elif op_type == "intersection":
                result = trimesh.boolean.intersection([base_mesh] + other_meshes, engine='scad')
        except Exception as e:
            self.chat_history.append(f"<b>Error:</b> Boolean operation failed: {e}. Fallback to simpler method if union.")
            if op_type == "union":
                try:
                    result = trimesh.util.concatenate([self.meshes[name] for name in mesh_names])
                    self.chat_history.append("<b>System:</b> Fallback: Concatenated meshes instead of solid CSG boolean.")
                except Exception:
                    return
            else:
                return
                
        for name in mesh_names:
            if name in self.meshes:
                del self.meshes[name]
                
        new_name = f"Bool_{op_type.capitalize()}_{base_name}"
        self.meshes[new_name] = result
        self.selected_mesh_name = new_name
        self.reset_creative_sliders()
        self.update_canvas()
        self.chat_history.append(f"<b>System:</b> Created boolean result '{new_name}'.")

    def creative_center_selected(self):
        """Aligns the selected shape to the absolute origin (0, 0, 0)."""
        if not self.selected_mesh_name: return
        self.save_state()
        mesh = self.meshes[self.selected_mesh_name]
        cx, cy, cz = mesh.centroid
        mesh.apply_translation([-cx, -cy, -cz])
        self.update_canvas()
        self.chat_history.append(f"<b>System:</b> Centered '{self.selected_mesh_name}' at origin.")

    def show_context_menu(self, position):
        """Allows independent removal and renaming via right-click."""
        item = self.object_list.itemAt(position)
        if not item: return
        self.select_from_list(item)

        menu = QtWidgets.QMenu()
        rename_act = menu.addAction("✎ Rename")
        delete_act = menu.addAction("🗑 Delete")
        dup_act = menu.addAction("👯 Duplicate")
        menu.addSeparator()

        solid_act = menu.addAction("✨ Make Solid (Reset)")

        # New Feature: Modification Suite
        tex_menu = menu.addMenu("🖼 Quick Texture")
        if self.pattern_functions:
            for tex_name in self.pattern_functions.keys():
                tex_menu.addAction(tex_name)

        mech_menu = menu.addMenu("🛠 Mechanical & Print Prep")
        t_piece_act = mech_menu.addAction("Add T-Piece Joint")
        bolt_hole_act = mech_menu.addAction("Add Integrated Bolt + Hole")
        peg_hole_act = mech_menu.addAction("Add Integrated Peg + Hole")
        drawer_act = mech_menu.addAction("📦 Add Integrated Drawer")
        lay_flat_act = mech_menu.addAction("📐 Lay Flat (Auto-Orient)")
        drop_bed_act = mech_menu.addAction("📐 Drop to Bed (Z=0)")
        repair_act = mech_menu.addAction("🩹 Repair Geometry (Heal)")
        intersect_act = menu.addAction("Intersection (Overlap Only)")

        # New Feature: Deformation Suite
        deform_menu = menu.addMenu("🌪 Deformations")
        twist_act = deform_menu.addAction("Twist")
        taper_act = deform_menu.addAction("Taper")
        bend_act = deform_menu.addAction("Bend")
        stretch_act = deform_menu.addAction("Stretch/Scale")
        bulge_act = deform_menu.addAction("Bulge / Swell")

        action = menu.exec(self.object_list.mapToGlobal(position))
        if action == rename_act:
            self.rename_selected()
        elif action == delete_act:
            self.delete_selected()
        elif action == dup_act:
            self.duplicate_selected()
        elif action == solid_act:
            self.make_selected_solid()
        elif action == t_piece_act:
            self.add_t_piece_at_selection()
        elif action == drawer_act:
            self.add_drawer_dialog()
        elif action == bolt_hole_act:
            self.add_bolt_with_hole_dialog()
        elif action == peg_hole_act:
            self.add_peg_with_hole_dialog()
        elif action == intersect_act:
            self.intersection_logic()
        elif action == lay_flat_act:
            self.lay_flat_selected()
        elif action == drop_bed_act:
            self.drop_to_bed_selected()
        elif action == repair_act:
            self.repair_selected()
        elif action == twist_act:
            self.deform_twist()
        elif action == taper_act:
            self.deform_taper()
        elif action == bend_act:
            self.deform_bend()
        elif action == stretch_act:
            self.deform_stretch()
        elif action == bulge_act:
            self.deform_bulge()
        elif action and action.parentWidget() == tex_menu:
            self.apply_texture_by_name(action.text())

    def rename_selected(self):
        """Renames the selected part to help keep the design organized."""
        if not self.selected_mesh_name: return
        old_name = self.selected_mesh_name
        new_name, ok = QtWidgets.QInputDialog.getText(self, "Rename Part", "New name:", text=old_name)
        if ok and new_name and new_name != old_name:
            if new_name in self.meshes:
                QtWidgets.QMessageBox.warning(self, "Error", "A part with this name already exists.")
                return
            self.meshes[new_name] = self.meshes.pop(old_name)
            self.selected_mesh_name = new_name
            self.update_canvas()

    def select_from_list(self, item):
        if item:
            self.selected_mesh_name = item.text()
            # Sync coordinate spinboxes
            if self.selected_mesh_name in self.meshes:
                mesh = self.meshes[self.selected_mesh_name]
                self.pos_x.blockSignals(True)
                self.pos_y.blockSignals(True)
                self.pos_z.blockSignals(True)
                self.pos_x.setValue(mesh.centroid[0])
                self.pos_y.setValue(mesh.centroid[1])
                self.pos_z.setValue(mesh.centroid[2])
                self.pos_x.blockSignals(False)
                self.pos_y.blockSignals(False)
                self.pos_z.blockSignals(False)
                self.reset_creative_sliders()
        self.update_canvas()

    def manual_move(self):
        """Moves all selected items in the list by the same relative amount."""
        selected_items = self.object_list.selectedItems()
        if not selected_items: return
        
        self.save_state()
        target = np.array([self.pos_x.value(), self.pos_y.value(), self.pos_z.value()])
        
        for item in selected_items:
            name = item.text()
            mesh = self.meshes[name]
            translation = target - mesh.centroid
            mesh.apply_translation(translation)
            # Update offset tracker for Smart Duplicate
            self.last_duplicate_offset = translation
            
        self.update_canvas()

    def manual_scale(self):
        """Scales the selected meshes by the factors in the spinboxes."""
        selected_items = self.object_list.selectedItems()
        if not selected_items: return
        
        self.save_state()
        sx = self.scale_x.value()
        sy = self.scale_y.value()
        sz = self.scale_z.value()
        
        for item in selected_items:
            name = item.text()
            mesh = self.meshes[name]
            centroid = mesh.centroid.copy()
            mesh.apply_translation(-centroid)
            scale_mat = np.diag([sx, sy, sz, 1.0])
            mesh.apply_transform(scale_mat)
            mesh.apply_translation(centroid)
            
        self.scale_x.blockSignals(True)
        self.scale_y.blockSignals(True)
        self.scale_z.blockSignals(True)
        self.scale_x.setValue(1.0)
        self.scale_y.setValue(1.0)
        self.scale_z.setValue(1.0)
        self.scale_x.blockSignals(False)
        self.scale_y.blockSignals(False)
        self.scale_z.blockSignals(False)
        self.update_canvas()

    def manual_rotate(self):
        """Rotates the selected meshes around their centroids by the angles in the spinboxes."""
        selected_items = self.object_list.selectedItems()
        if not selected_items: return
        
        self.save_state()
        rx = np.radians(self.rot_x.value())
        ry = np.radians(self.rot_y.value())
        rz = np.radians(self.rot_z.value())
        
        for item in selected_items:
            name = item.text()
            mesh = self.meshes[name]
            centroid = mesh.centroid.copy()
            mesh.apply_translation(-centroid)
            rot_mat = trimesh.transformations.euler_matrix(rx, ry, rz)
            mesh.apply_transform(rot_mat)
            mesh.apply_translation(centroid)
            
        self.rot_x.blockSignals(True)
        self.rot_y.blockSignals(True)
        self.rot_z.blockSignals(True)
        self.rot_x.setValue(0.0)
        self.rot_y.setValue(0.0)
        self.rot_z.setValue(0.0)
        self.rot_x.blockSignals(False)
        self.rot_y.blockSignals(False)
        self.rot_z.blockSignals(False)
        self.update_canvas()

    def delete_selected(self):
        if self.selected_mesh_name in self.meshes:
            del self.meshes[self.selected_mesh_name]
            self.selected_mesh_name = None
            self.update_canvas()

    def draw_build_plate(self):
        """Visualizes the 220x220mm build area of the Flashforge AD5X."""
        grid = pv.Plane(i_size=self.BUILD_LIMITS[0], j_size=self.BUILD_LIMITS[1])
        # Offset slightly downwards to prevent Z-fighting and show models sitting clearly on top
        grid.points[:, 2] -= 0.1
        self.plotter.add_mesh(grid, color="black", opacity=0.3, show_edges=True, name="build_plate")

    def init_toolbar(self):
        """Creates the shape library and basic file operations."""
        self.toolbar = QtWidgets.QToolBar("Tools")
        self.addToolBar(QtCore.Qt.ToolBarArea.TopToolBarArea, self.toolbar)

        # 1. Shapes Menu
        shapes_btn = QtWidgets.QToolButton(); shapes_btn.setText("🧊 Create")
        shapes_btn.setPopupMode(QtWidgets.QToolButton.ToolButtonPopupMode.InstantPopup)
        shapes_menu = QtWidgets.QMenu()
        for s in ["Cube", "Sphere", "Cylinder", "Cone", "Pyramid", "Torus", "Capsule", "Annulus", "Helix", "Torus Knot", "Star", "Heart", "Hex Prism", "Oct Prism", "Bolt", "Nut", "Sketch Mode"]:
            shapes_menu.addAction(s).triggered.connect(lambda chk, val=s: self.add_primitive(val))
        
        shapes_menu.addSeparator()
        math_menu = shapes_menu.addMenu("📐 Math Art Shapes")
        math_menu.addAction("Möbius Strip").triggered.connect(lambda: self.add_math_shape("mobius"))
        math_menu.addAction("Klein Bottle").triggered.connect(lambda: self.add_math_shape("klein"))
        math_menu.addAction("Gyroid Infill").triggered.connect(lambda: self.add_math_shape("gyroid"))
        math_menu.addAction("Chaos Attractor Ribbon").triggered.connect(lambda: self.add_math_shape("lorenz"))
        math_menu.addAction("Sierpinski Fractal Pyramid").triggered.connect(lambda: self.add_math_shape("sierpinski"))
        
        shapes_menu.addSeparator()
        shapes_menu.addAction("🖼 Image-to-3D (AI)").triggered.connect(self.import_photos_to_3d)
        shapes_btn.setMenu(shapes_menu)
        self.toolbar.addWidget(shapes_btn)

        # 2. Modify Menu (Mechanical & Boolean)
        mod_btn = QtWidgets.QToolButton(); mod_btn.setText("🛠 Modify")
        mod_btn.setPopupMode(QtWidgets.QToolButton.ToolButtonPopupMode.InstantPopup)
        mod_menu = QtWidgets.QMenu()
        mod_menu.addAction("Merge (Union)").triggered.connect(self.merge_all_meshes)
        mod_menu.addAction("Subtract (Hole)").triggered.connect(self.subtract_logic)
        mod_menu.addAction("Intersection").triggered.connect(self.intersection_logic)
        mod_menu.addSeparator()
        mod_menu.addAction("Duplicate").triggered.connect(self.duplicate_selected)
        mod_menu.addAction("👯 Mirror (X-Axis)").triggered.connect(lambda: self.mirror_mesh([1,0,0]))
        mod_menu.addAction("👯 Mirror (Y-Axis)").triggered.connect(lambda: self.mirror_mesh([0,1,0]))
        mod_menu.addAction("📏 Linear Array").triggered.connect(self.create_linear_array)
        mod_menu.addAction("Align Parts").triggered.connect(self.align_selected_dialog)
        mod_menu.addAction("Center All").triggered.connect(self.center_all_meshes)
        mod_btn.setMenu(mod_menu)
        self.toolbar.addWidget(mod_btn)

        # 3. View Menu
        view_btn = QtWidgets.QToolButton(); view_btn.setText("👁 View")
        view_btn.setPopupMode(QtWidgets.QToolButton.ToolButtonPopupMode.InstantPopup)
        view_menu = QtWidgets.QMenu()
        view_menu.addAction("Isometric").triggered.connect(lambda: self.plotter.view_isometric())
        view_menu.addAction("Top View").triggered.connect(lambda: self.plotter.view_xy())
        view_menu.addAction("Front View").triggered.connect(lambda: self.plotter.view_xz())
        view_menu.addAction("Side View").triggered.connect(lambda: self.plotter.view_yz())
        view_menu.addSeparator()
        view_menu.addAction("Wireframe Mode").triggered.connect(lambda: self.set_shading_mode("wireframe"))
        view_menu.addAction("Solid Surface").triggered.connect(lambda: self.set_shading_mode("surface"))
        view_menu.addAction("Surface + Edges").triggered.connect(lambda: self.set_shading_mode("edges"))
        
        view_menu.addSeparator()
        style_menu = view_menu.addMenu("✨ Aesthetic Styles")
        style_menu.addAction("✨ Default Material").triggered.connect(lambda: self.apply_aesthetic_shader("default"))
        style_menu.addAction("🏆 Polished Gold").triggered.connect(lambda: self.apply_aesthetic_shader("gold"))
        style_menu.addAction("💿 Liquid Chrome").triggered.connect(lambda: self.apply_aesthetic_shader("chrome"))
        style_menu.addAction("💎 Frosted Glass (X-Ray)").triggered.connect(lambda: self.apply_aesthetic_shader("glass"))
        style_menu.addAction("🔴 Holographic Neon").triggered.connect(lambda: self.apply_aesthetic_shader("neon"))
        style_menu.addAction("🏺 Sculptor Clay").triggered.connect(lambda: self.apply_aesthetic_shader("clay"))
        
        view_btn.setMenu(view_menu)
        self.toolbar.addWidget(view_btn)

        self.toolbar.addSeparator()

        undo_act = self.toolbar.addAction("↩ Undo")
        undo_act.setShortcut("Ctrl+Z"); undo_act.triggered.connect(self.undo)
        redo_act = self.toolbar.addAction("↪ Redo")
        redo_act.setShortcut("Ctrl+Y"); redo_act.triggered.connect(self.redo)
        
        self.gizmo_act = self.toolbar.addAction("🎮 Advanced Gizmo")
        self.gizmo_act.setCheckable(True)
        self.gizmo_act.triggered.connect(self.toggle_affine_widget)

        self.box_widget_act = self.toolbar.addAction("📦 Resize Box")
        self.box_widget_act.setCheckable(True)
        self.box_widget_act.triggered.connect(self.toggle_transform_widget)

        self.toolbar.addSeparator()
        ghost_act = self.toolbar.addAction("👻 Ghost Mode")
        ghost_act.setCheckable(True); ghost_act.triggered.connect(self.toggle_ghost_mode)

        self.toolbar.addAction("💾 Save Project").triggered.connect(self.save_project)
        self.toolbar.addAction("📂 Open Project").triggered.connect(self.load_project)
        self.toolbar.addSeparator()
        self.toolbar.addAction("📥 Import").triggered.connect(self.import_3d_model)
        self.toolbar.addAction("📤 Export 3MF").triggered.connect(self.export_to_3mf)
        self.toolbar.addAction("📤 Export STL").triggered.connect(self.export_to_stl)
        self.toolbar.addAction("📤 Export OBJ").triggered.connect(self.export_to_obj)
    def init_art_palette(self):
        """Creates the visual texture and color bonding sidebar."""
        palette_group = QtWidgets.QGroupBox("Art & Texture Palette")
        palette_layout = QtWidgets.QVBoxLayout()

        # NEW: Default Texture Selector
        palette_layout.addWidget(QtWidgets.QLabel("Default Texture for New Items:"))
        self.default_tex_combo = QtWidgets.QComboBox()
        self.default_tex_combo.addItems(["None"] + list(self.pattern_functions.keys()))
        palette_layout.addWidget(self.default_tex_combo)

        # NEW: Targeted Selection / Creation Mode
        self.tex_as_object_cb = QtWidgets.QCheckBox("Create Texture as Independent Piece")
        self.tex_as_object_cb.setToolTip("If checked, patterns create a new 'Base' instead of modifying selection")
        palette_layout.addWidget(self.tex_as_object_cb)

        self.area_mode_btn = QtWidgets.QPushButton("🎯 Toggle Area Selection (Brush)")
        self.area_mode_btn.setCheckable(True)
        self.area_mode_btn.clicked.connect(self.toggle_selection_mode)
        palette_layout.addWidget(self.area_mode_btn)

        self.sculpt_mode_btn = QtWidgets.QPushButton("💪 Pull/Sculpt Surface")
        self.sculpt_mode_btn.setCheckable(True)
        self.sculpt_mode_btn.setToolTip("Click a point to pull the geometry outward")
        self.sculpt_mode_btn.clicked.connect(self.toggle_sculpt_mode)
        palette_layout.addWidget(self.sculpt_mode_btn)

        # Density / Resolution Slider
        palette_layout.addWidget(QtWidgets.QLabel("Geometric Density (Resolution)"))
        self.density_slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        self.density_slider.setMinimum(0)
        self.density_slider.setMaximum(3)
        self.density_slider.setValue(1)
        self.density_slider.setTickPosition(QtWidgets.QSlider.TickPosition.TicksBelow)
        self.density_slider.valueChanged.connect(self.update_density)
        palette_layout.addWidget(self.density_slider)
        
        # Color Bonding Section
        color_label = QtWidgets.QLabel("Color Bond (Two-Tone Merge)")
        palette_layout.addWidget(color_label)
        
        color_btn_layout = QtWidgets.QHBoxLayout()
        self.c1_btn = QtWidgets.QPushButton()
        self.c1_btn.setStyleSheet(f"background-color: {self.current_colors[0].name()}; height: 30px;")
        self.c1_btn.clicked.connect(lambda: self.pick_color(0))
        
        self.c2_btn = QtWidgets.QPushButton()
        self.c2_btn.setStyleSheet(f"background-color: {self.current_colors[1].name()}; height: 30px;")
        self.c2_btn.clicked.connect(lambda: self.pick_color(1))
        
        color_btn_layout.addWidget(self.c1_btn)
        color_btn_layout.addWidget(self.c2_btn)
        palette_layout.addLayout(color_btn_layout)
        
        apply_bond_btn = QtWidgets.QPushButton("Apply Color Bond")
        apply_bond_btn.clicked.connect(self.apply_color_bond)
        palette_layout.addWidget(apply_bond_btn)

        palette_layout.addSpacing(20)
        palette_layout.addWidget(QtWidgets.QLabel("Physical Textures & Patterns"))

        # Texture Icon Grid
        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        container = QtWidgets.QWidget()
        grid = QtWidgets.QGridLayout(container)

        # Add a "Clear Selection" button to the top of the grid
        clear_pick_btn = QtWidgets.QPushButton("Clear Selection")
        clear_pick_btn.clicked.connect(self.clear_selection)
        palette_layout.addWidget(clear_pick_btn)
        
        # Automatically generate buttons for all textures registered in the logic registry
        for i, name in enumerate(self.pattern_functions.keys()):
            btn = QtWidgets.QToolButton()
            btn.setText(name)
            btn.setToolButtonStyle(QtCore.Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
            
            # Generate a procedural icon for the "Art Kid" dream vibe
            pixmap = QtGui.QPixmap(64, 64)
            pixmap.fill(QtGui.QColor("darkgray"))
            painter = QtGui.QPainter(pixmap)
            painter.setPen(QtGui.QColor("white"))
            if name in ["Stucco", "Sand", "Leather"]:
                for _ in range(100): painter.drawPoint(np.random.randint(0,64), np.random.randint(0,64))
            elif name == "Ridges":
                for j in range(0, 64, 8): painter.drawLine(0, j, 64, j)
            elif name in ["Waves", "Spiral", "Archimedean"]:
                painter.drawEllipse(10, 10, 40, 40)
            elif name == "Crumpled":
                for _ in range(200): painter.drawPoint(np.random.randint(0,64), np.random.randint(0,64))
            elif name in ["Plaid", "Knurl", "Honeycomb", "Diamond"]:
                for j in range(0, 64, 8):
                    painter.drawLine(0, j, 64, j)
                    painter.drawLine(j, 0, j, 64)
            elif name == "ZigZag":
                for x in range(0, 64, 10):
                    painter.drawLine(x, 0, x+5, 64); painter.drawLine(x+5, 64, x+10, 0)
            elif name == "Chevron":
                for y in range(0, 64, 16):
                    painter.drawPolyline([QtCore.QPoint(0, y), QtCore.QPoint(32, y+10), QtCore.QPoint(64, y)])
            elif name == "Thread":
                for y in range(8, 64, 12):
                    painter.drawLine(10, y, 54, y - 6)
            elif name == "Octagram":
                painter.drawPolygon([QtCore.QPoint(32,0), QtCore.QPoint(42,22), QtCore.QPoint(64,32), QtCore.QPoint(42,42), QtCore.QPoint(32,64), QtCore.QPoint(22,42), QtCore.QPoint(0,32), QtCore.QPoint(22,22)])
            elif name == "Gyroid":
                painter.drawArc(10, 10, 40, 40, 0, 180*16); painter.drawArc(10, 20, 40, 40, 180*16, 180*16)
            elif name == "Rectilinear":
                for j in range(0, 64, 12): painter.drawLine(0, j, 64, j)
                for j in range(0, 64, 12): painter.drawLine(j, 0, j, 64)
            elif name == "Polka":
                for x in range(8, 64, 16):
                    for y in range(8, 64, 16): painter.drawEllipse(x, y, 4, 4)
            elif name in ["Brick", "Grooves"]:
                for y in range(0, 64, 12):
                    painter.drawLine(0, y, 64, y)
                    offset = 15 if (y // 12) % 2 == 0 else 0
                    for x in range(offset, 64, 30): painter.drawLine(x, y, x, y + 12)
            elif name in ["Wood", "Voronoi", "Pebbles"]:
                 for r in range(5, 60, 10): painter.drawEllipse(32-r//2, 32-r//2, r, r)
            elif name == "Carbon":
                painter.drawRect(10, 10, 20, 20); painter.drawRect(34, 34, 20, 20)
            else:
                for _ in range(100): painter.drawPoint(np.random.randint(0,64), np.random.randint(0,64))
            painter.end()
            
            btn.setIcon(QtGui.QIcon(pixmap))
            btn.setIconSize(QtCore.QSize(64, 64))
            btn.clicked.connect(lambda checked, n=name: self.apply_texture_by_name(n))
            grid.addWidget(btn, i // 2, i % 2)

        scroll.setWidget(container)
        palette_layout.addWidget(scroll)
        palette_group.setLayout(palette_layout)
        self.right_sidebar.addWidget(palette_group)

    def handle_click(self, point):
        """Handles mouse clicks on the 3D model for area-based texturing."""
        if not self.selected_mesh_name: return
        mesh = self.meshes[self.selected_mesh_name]

        if self.area_mode_btn.isChecked():
            # Calculate distance from click to all vertices
            dists = np.linalg.norm(mesh.vertices - point, axis=1)
            self.active_selection_indices = np.where(dists < 15.0)[0]
            self.chat_history.append(f"<b>System:</b> Selected {len(self.active_selection_indices)} vertices near click point.")
        elif self.sculpt_mode_btn.isChecked():
            # Sculpting 'Pull' logic: move vertices near click point outward
            dists = np.linalg.norm(mesh.vertices - point, axis=1)
            indices = np.where(dists < 20.0)[0]
            if len(indices) > 0:
                # Pull direction: outward from center through point
                direction = point - mesh.centroid
                norm = np.linalg.norm(direction)
                if norm > 0:
                    direction /= norm
                    mesh.vertices[indices] += direction * 8.0 
                    self.update_canvas()
                    self.chat_history.append("<b>System:</b> Pulled surface section outward.")

    def on_mesh_picked(self, mesh_data):
        """Selects an object and updates the Technical Inspector."""
        if mesh_data is None: return
        for name, mesh in self.meshes.items():
            if np.allclose(mesh.bounds, mesh_data.bounds, atol=0.5):
                self.selected_mesh_name = name
                self.update_canvas()
                
                # Sync coordinate spinboxes
                if hasattr(self, 'pos_x'):
                    self.pos_x.blockSignals(True)
                    self.pos_y.blockSignals(True)
                    self.pos_z.blockSignals(True)
                    self.pos_x.setValue(mesh.centroid[0])
                    self.pos_y.setValue(mesh.centroid[1])
                    self.pos_z.setValue(mesh.centroid[2])
                    self.pos_x.blockSignals(False)
                    self.pos_y.blockSignals(False)
                    self.pos_z.blockSignals(False)
                
                self.reset_creative_sliders()
                    
                ext = mesh.extents
                vol = mesh.volume / 1000.0 # Convert to cm3
                if hasattr(self, 'status_bar') and self.status_bar:
                    self.status_bar.showMessage(f"Selected: {name} | Size: {ext[0]:.1f}x{ext[1]:.1f}x{ext[2]:.1f}mm | Volume: {vol:.2f}cm³")
                break

    def _on_key_press(self, obj, event):
        """Standard professional hotkeys for rapid workflow."""
        key = self.plotter.iren.GetKeySym()
        if key == "Delete":
            self.delete_selected()
        elif key == "d" and self.plotter.iren.GetControlKey():
            self.duplicate_selected()
        elif key == "z" and self.plotter.iren.GetControlKey():
            self.undo()
        elif key == "y" and self.plotter.iren.GetControlKey():
            self.redo()

    def set_shading_mode(self, mode):
        """Toggles rendering styles for technical inspection."""
        for name in self.meshes:
            if name in self.plotter.renderer.actors:
                actor = self.plotter.renderer.actors[name]
                actor.prop.style = mode if mode != "edges" else "surface"
                actor.prop.show_edges = (mode == "edges")
        self.plotter.render()

    def mirror_mesh(self, normal):
        """Reflects a part across a plane, useful for symmetric mechanical designs."""
        if not self.selected_mesh_name: return
        self.save_state()
        mesh = self.meshes[self.selected_mesh_name]
        # Reflect across the centroid using the provided axis normal
        mesh.apply_transform(trimesh.transformations.reflection_matrix(mesh.centroid, normal))
        self.update_canvas()
        self.chat_history.append(f"<b>System:</b> Mirrored '{self.selected_mesh_name}' across axis.")

    def create_linear_array(self):
        """Clones an object multiple times along the X-axis for structural patterns."""
        if not self.selected_mesh_name: return
        count, ok = QtWidgets.QInputDialog.getInt(self, "Linear Array", "Number of copies:", 3, 2, 50)
        if not ok: return
        dist, ok2 = QtWidgets.QInputDialog.getDouble(self, "Linear Array", "Spacing (mm):", 50.0, 1.0, 500.0)
        if ok2:
            self.save_state()
            source = self.meshes[self.selected_mesh_name]
            for i in range(1, count):
                new_mesh = source.copy()
                new_mesh.apply_translation([dist * i, 0, 0])
                self.meshes[f"{self.selected_mesh_name}_Arr_{i}"] = new_mesh
            self.update_canvas()
            self.chat_history.append(f"<b>System:</b> Generated array of {count} parts.")

    def toggle_affine_widget(self, enabled):
        """Standard CAD gizmo for high-precision dragging/rotating."""
        self.plotter.clear_widgets()
        self.widget_bound_mesh_name = None
        if enabled:
            if hasattr(self, 'box_widget_act'):
                self.box_widget_act.setChecked(False)
            if hasattr(self, 'widget_start_mesh'):
                delattr(self, 'widget_start_mesh')
            self.refresh_widgets()

    def save_state(self):
        """Snapshots current scene for undo functionality."""
        snapshot = {name: mesh.copy() for name, mesh in self.meshes.items()}
        self.undo_stack.append(snapshot)
        self.redo_stack.clear() # New actions break the redo chain
        if len(self.undo_stack) > 20: self.undo_stack.pop(0)

    def undo(self):
        """Restores last saved scene state."""
        if not self.undo_stack: return
        current_state = {name: mesh.copy() for name, mesh in self.meshes.items()}
        self.redo_stack.append(current_state)
        self.meshes = self.undo_stack.pop()
        self.update_canvas()
        self.chat_history.append("<b>System:</b> Undo successful.")

    def lay_flat_selected(self):
        """Automatically rotates the mesh to its most stable orientation for 3D printing."""
        if not self.selected_mesh_name: return
        self.save_state()
        mesh = self.meshes[self.selected_mesh_name]
        stable_poses, _ = mesh.compute_stable_poses()
        if len(stable_poses) > 0:
            mesh.apply_transform(stable_poses[0])
            # Snap to floor (Z=0)
            mesh.apply_translation([0, 0, -mesh.bounds[0][2]])
            self.update_canvas()
            self.chat_history.append(f"<b>System:</b> Auto-oriented '{self.selected_mesh_name}' to floor.")

    def drop_to_bed_selected(self):
        """Snaps the selected mesh's lowest Z point to the build plate (Z=0)."""
        if not self.selected_mesh_name: return
        self.save_state()
        mesh = self.meshes[self.selected_mesh_name]
        z_min = mesh.bounds[0][2]
        mesh.apply_translation([0, 0, -z_min])
        self.update_canvas()
        self.chat_history.append(f"<b>System:</b> Snapped '{self.selected_mesh_name}' to the print bed (Z=0).")

    def repair_selected(self):
        """Standard professional geometry healing (fixing holes and normals)."""
        if not self.selected_mesh_name: return
        self.save_state()
        mesh = self.meshes[self.selected_mesh_name]
        mesh.fill_holes()
        mesh.fix_normals()
        mesh.remove_duplicate_faces()
        self.update_canvas()
        self.chat_history.append(f"<b>System:</b> Geometry healing complete for '{self.selected_mesh_name}'.")

    def redo(self):
        """Restores state from redo stack."""
        if not self.redo_stack: return
        # Save current state for undo manually without clearing redo_stack
        snapshot = {name: mesh.copy() for name, mesh in self.meshes.items()}
        self.undo_stack.append(snapshot)
        if len(self.undo_stack) > 20: self.undo_stack.pop(0)
        
        self.meshes = self.redo_stack.pop()
        self.update_canvas()
        self.chat_history.append("<b>System:</b> Redo successful.")

    def toggle_ghost_mode(self, enabled):
        """Makes all meshes semi-transparent to see internal alignments."""
        opacity = 0.3 if enabled else 1.0
        for name in self.meshes:
            self.plotter.renderer.actors[name].prop.opacity = opacity
        self.plotter.render()

    def intersection_logic(self):
        """Keeps only the volume where parts overlap."""
        selected_items = self.object_list.selectedItems()
        if len(selected_items) < 2: 
            self.chat_history.append("<b>System:</b> Select at least 2 parts to find their intersection.")
            return
        self.save_state()
        try:
            target_meshes = [self.meshes[item.text()] for item in selected_items]
            intersected = trimesh.boolean.intersection(target_meshes)
            for item in selected_items:
                del self.meshes[item.text()]
            name = f"Intersection_{len(self.meshes)}"
            self.meshes[name] = intersected
            self.selected_mesh_name = name
            self.update_canvas()
            self.chat_history.append("<b>System:</b> Intersection calculated.")
        except Exception as e:
            self.chat_history.append(f"<b>Error:</b> Intersection failed: {str(e)}")

    def get_mouse_xy_projection(self, pos):
        """Projects screen coordinates (x, y) onto the Z=0 plane (build plate) using camera raycasting."""
        renderer = self.plotter.renderer
        renderer.SetDisplayPoint(pos[0], pos[1], 0.0)
        renderer.DisplayToWorld()
        near_world = np.array(renderer.GetWorldPoint()[:3])
        
        renderer.SetDisplayPoint(pos[0], pos[1], 1.0)
        renderer.DisplayToWorld()
        far_world = np.array(renderer.GetWorldPoint()[:3])
        
        dir_z = far_world[2] - near_world[2]
        if abs(dir_z) > 1e-6:
            t = -near_world[2] / dir_z
            return near_world + t * (far_world - near_world)
        return near_world

    def _on_drag_start(self, obj, event):
        """Starts a drag operation if Shift is held and a mesh is clicked."""
        if (hasattr(self, 'box_widget_act') and self.box_widget_act.isChecked()) or \
           (hasattr(self, 'gizmo_act') and self.gizmo_act.isChecked()):
            self.save_state()

        if not self.plotter.iren.GetShiftKey():
            return
            
        pos = self.plotter.iren.GetEventPosition()
        picker = pv.vtk.vtkPropPicker()
        picker.Pick(pos[0], pos[1], 0, self.plotter.renderer)
        actor = picker.GetActor()
        
        if actor:
            for name, m in self.meshes.items():
                if self.plotter.renderer.actors.get(name) == actor:
                    self.selected_mesh_name = name
                    self.save_state()
                    self.is_dragging = True
                    self.drag_start_world = self.get_mouse_xy_projection(pos)
                    obj.AbortFlagOn()
                    return

    def _on_drag_move(self, obj, event):
        """Translates the mesh on the XY plane during dragging."""
        if self.is_dragging and self.selected_mesh_name:
            pos = self.plotter.iren.GetEventPosition()
            current_world = self.get_mouse_xy_projection(pos)
            
            delta = current_world - self.drag_start_world
            delta[2] = 0 
            
            if self.snap_to_grid:
                delta = np.round(delta / 5.0) * 5.0
            
            if np.linalg.norm(delta) > 0.1:
                mesh = self.meshes[self.selected_mesh_name]
                mesh.apply_translation(delta)
                self.drag_start_world = self.drag_start_world + delta
                self.update_canvas()
            obj.AbortFlagOn()

    def _on_drag_end(self, obj, event):
        """Stops the drag operation."""
        if self.is_dragging:
            self.is_dragging = False
            self.chat_history.append(f"<b>System:</b> Shift-Drag completed for '{self.selected_mesh_name}'.")
            
        if hasattr(self, 'box_widget_act') and self.box_widget_act.isChecked() and self.selected_mesh_name:
            self.widget_start_mesh = self.meshes[self.selected_mesh_name].copy()
            self.widget_bound_mesh_name = None
            self.refresh_widgets()

    def toggle_transform_widget(self, enabled):
        """Enables/Disables interactive box handles for moving/scaling pieces."""
        self.plotter.clear_widgets()
        self.widget_bound_mesh_name = None
        if enabled:
            if hasattr(self, 'gizmo_act'):
                self.gizmo_act.setChecked(False)
            self.refresh_widgets()
        else:
            if hasattr(self, 'widget_start_mesh'):
                delattr(self, 'widget_start_mesh')

    def apply_widget_transform(self, box_polydata):
        """Syncs the box widget movements and scaling back to the trimesh object."""
        if not self.selected_mesh_name or not hasattr(self, 'widget_start_mesh'): return
        
        orig_mesh = self.widget_start_mesh.copy()
        new_center = np.array(box_polydata.center)
        b = box_polydata.bounds
        new_extents = np.array([b[1] - b[0], b[3] - b[2], b[5] - b[4]])
        
        orig_extents = orig_mesh.extents
        scale_factors = np.ones(3)
        for i in range(3):
            if orig_extents[i] > 1e-5:
                scale_factors[i] = new_extents[i] / orig_extents[i]
        
        centroid = orig_mesh.centroid.copy()
        orig_mesh.apply_translation(-centroid)
        orig_mesh.apply_transform(np.diag(list(scale_factors) + [1.0]))
        orig_mesh.apply_translation(new_center)
        
        self.meshes[self.selected_mesh_name] = orig_mesh
        
        if hasattr(self, 'pos_x'):
            self.pos_x.blockSignals(True)
            self.pos_y.blockSignals(True)
            self.pos_z.blockSignals(True)
            self.pos_x.setValue(new_center[0])
            self.pos_y.setValue(new_center[1])
            self.pos_z.setValue(new_center[2])
            self.pos_x.blockSignals(False)
            self.pos_y.blockSignals(False)
            self.pos_z.blockSignals(False)
        
        self.update_canvas()

    def apply_affine_transform(self, matrix):
        """Syncs the affine widget (gizmo) movements back to the trimesh object."""
        if not self.selected_mesh_name or not hasattr(self, 'widget_start_mesh'): return
        
        self.save_state()  # Save scene state for undo before modifying!
        orig_mesh = self.widget_start_mesh.copy()
        orig_mesh.apply_transform(matrix)
        self.meshes[self.selected_mesh_name] = orig_mesh
        
        # Sync coordinate spinboxes
        if hasattr(self, 'pos_x'):
            self.pos_x.blockSignals(True)
            self.pos_y.blockSignals(True)
            self.pos_z.blockSignals(True)
            self.pos_x.setValue(orig_mesh.centroid[0])
            self.pos_y.setValue(orig_mesh.centroid[1])
            self.pos_z.setValue(orig_mesh.centroid[2])
            self.pos_x.blockSignals(False)
            self.pos_y.blockSignals(False)
            self.pos_z.blockSignals(False)
            
        # Update start mesh and sync the canvas
        self.widget_start_mesh = orig_mesh.copy()
        self.update_canvas()

    def refresh_widgets(self):
        """Recreates the active widget for the currently selected mesh if it changed."""
        if not hasattr(self, 'gizmo_act') or not hasattr(self, 'box_widget_act'):
            return
            
        if not hasattr(self, 'widget_bound_mesh_name'):
            self.widget_bound_mesh_name = None
            
        if self.selected_mesh_name == self.widget_bound_mesh_name:
            return
            
        self.plotter.clear_widgets()
        self.widget_bound_mesh_name = self.selected_mesh_name
        
        if not self.selected_mesh_name:
            return
            
        if self.gizmo_act.isChecked():
            actor = self.plotter.renderer.actors.get(self.selected_mesh_name)
            if actor: 
                self.widget_start_mesh = self.meshes[self.selected_mesh_name].copy()
                self.plotter.add_affine_transform_widget(actor, release_callback=self.apply_affine_transform)
        elif self.box_widget_act.isChecked():
            self.widget_start_mesh = self.meshes[self.selected_mesh_name].copy()
            mesh = self.meshes[self.selected_mesh_name]
            self.plotter.add_box_widget(callback=self.apply_widget_transform, bounds=pv.wrap(mesh).bounds)

    def add_t_piece_at_selection(self):
        """Adds a T-shaped joint at the selected object's location."""
        if not self.selected_mesh_name: return
        c1 = trimesh.creation.cylinder(radius=4, height=40)
        c2 = trimesh.creation.cylinder(radius=4, height=25)
        c2.apply_transform(trimesh.transformations.rotation_matrix(np.pi/2, [1,0,0]))
        t_joint = trimesh.util.concatenate([c1, c2])
        pos = self.meshes[self.selected_mesh_name].centroid
        t_joint.apply_translation(pos + [30, 0, 0]) 
        name = f"T_Joint_{len(self.meshes)}"
        self.meshes[name] = t_joint
        self.update_canvas()
        self.chat_history.append(f"<b>System:</b> Added T-Piece near {self.selected_mesh_name}.")

    def make_selected_solid(self):
        """Removes colors and attempts to flatten textures on the selected mesh."""
        if not self.selected_mesh_name: return
        mesh = self.meshes[self.selected_mesh_name]
        if hasattr(mesh.visual, 'vertex_colors'):
            mesh.visual.vertex_colors = np.full((len(mesh.vertices), 4), 255, dtype=np.uint8)
        trimesh.smoothing.filter_laplacian(mesh, iterations=20)
        self.update_canvas()
        self.chat_history.append(f"<b>System:</b> '{self.selected_mesh_name}' set to Solid state.")

    def deform_twist(self):
        """Twists the mesh vertices around its vertical center."""
        if not self.selected_mesh_name: return
        val, ok = QtWidgets.QInputDialog.getDouble(self, "Twist", "Amount (degrees per unit height):", 5.0, -360, 360)
        if ok:
            mesh = self.meshes[self.selected_mesh_name]
            angle_rad = np.radians(val)
            z = mesh.vertices[:, 2]; z_min = z.min()
            cx, cy = mesh.centroid[0], mesh.centroid[1]
            x = mesh.vertices[:, 0] - cx
            y = mesh.vertices[:, 1] - cy
            theta = angle_rad * (z - z_min)
            c, s = np.cos(theta), np.sin(theta)
            mesh.vertices[:, 0] = cx + (x * c - y * s)
            mesh.vertices[:, 1] = cy + (x * s + y * c)
            self.update_canvas()
            self.chat_history.append(f"<b>System:</b> Applied {val} degree twist to {self.selected_mesh_name}.")

    def deform_taper(self):
        """Tapers the object so the top is smaller or larger than the bottom."""
        if not self.selected_mesh_name: return
        val, ok = QtWidgets.QInputDialog.getDouble(self, "Taper", "Top Scale Factor (e.g. 0.5):", 0.5, 0.0, 10.0)
        if ok:
            mesh = self.meshes[self.selected_mesh_name]
            z = mesh.vertices[:, 2]; z_min, z_max = z.min(), z.max()
            if z_max == z_min: return
            cx, cy = mesh.centroid[0], mesh.centroid[1]
            x = mesh.vertices[:, 0] - cx
            y = mesh.vertices[:, 1] - cy
            factor = 1.0 + (val - 1.0) * (z - z_min) / (z_max - z_min)
            mesh.vertices[:, 0] = cx + x * factor
            mesh.vertices[:, 1] = cy + y * factor
            self.update_canvas()
            self.chat_history.append(f"<b>System:</b> Applied taper factor {val} to {self.selected_mesh_name}.")

    def deform_bend(self):
        """Bends the object along a radius based on height."""
        if not self.selected_mesh_name: return
        val, ok = QtWidgets.QInputDialog.getDouble(self, "Bend", "Angle (degrees):", 45.0, -180, 180)
        if ok and abs(val) > 0.1:
            mesh = self.meshes[self.selected_mesh_name]
            z = mesh.vertices[:, 2]; z_min, z_max = z.min(), z.max()
            height = z_max - z_min
            angle_rad = np.radians(val)
            R = height / angle_rad
            cx = mesh.centroid[0]
            x_rel = mesh.vertices[:, 0] - cx
            theta = (z - z_min) / R
            mesh.vertices[:, 0] = cx + (R + x_rel) * np.cos(theta) - R
            mesh.vertices[:, 2] = z_min + (R + x_rel) * np.sin(theta)
            self.update_canvas()
            self.chat_history.append(f"<b>System:</b> Applied {val} degree bend to {self.selected_mesh_name}.")

    def deform_stretch(self):
        """Scales the object along a specific axis."""
        if not self.selected_mesh_name: return
        axes = ["X", "Y", "Z"]
        axis, ok = QtWidgets.QInputDialog.getItem(self, "Stretch", "Select Axis:", axes, 2, False)
        if ok:
            factor, ok2 = QtWidgets.QInputDialog.getDouble(self, "Stretch", "Factor:", 1.5, 0.1, 10.0)
            if ok2:
                mesh = self.meshes[self.selected_mesh_name]
                scale = np.eye(4); scale[axes.index(axis), axes.index(axis)] = factor
                mesh.apply_transform(scale)
                self.update_canvas()
                self.chat_history.append(f"<b>System:</b> Stretched {self.selected_mesh_name} by factor {factor} on {axis} axis.")

    def deform_bulge(self):
        """Bulges or shrinks the object in the middle."""
        if not self.selected_mesh_name: return
        val, ok = QtWidgets.QInputDialog.getDouble(self, "Bulge / Swell", "Bulge Factor (positive to swell, negative to shrink):", 0.3, -2.0, 2.0)
        if ok:
            self.save_state()
            mesh = self.meshes[self.selected_mesh_name]
            z = mesh.vertices[:, 2]; z_min, z_max = z.min(), z.max()
            if z_max == z_min: return
            height = z_max - z_min
            cx, cy = mesh.centroid[0], mesh.centroid[1]
            x = mesh.vertices[:, 0] - cx
            y = mesh.vertices[:, 1] - cy
            z_norm = (z - z_min) / height
            envelope = np.sin(z_norm * np.pi)
            factor = 1.0 + val * envelope
            mesh.vertices[:, 0] = cx + x * factor
            mesh.vertices[:, 1] = cy + y * factor
            self.update_canvas()
            self.chat_history.append(f"<b>System:</b> Applied bulge factor {val} to {self.selected_mesh_name}.")

    def clear_selection(self):
        self.active_selection_indices = None
        self.plotter.remove_selection()
        self.chat_history.append("<b>System:</b> Selection cleared. Textures will apply to whole object.")

    def toggle_selection_mode(self, enabled):
        self.plotter.disable_picking() # Disable any active picker
        if not enabled:
            self.clear_selection()
            self.plotter.enable_mesh_picking(callback=self.on_mesh_picked, show=False) # Re-enable default mesh picking
        else:
            self.sculpt_mode_btn.setChecked(False) # Ensure sculpt mode is off
            self.plotter.enable_point_picking(callback=self.handle_click, show_message=False, color="pink")
            self.chat_history.append("<b>System:</b> Selection Mode (Brush) Active. Click model to define area.")

    def toggle_sculpt_mode(self, enabled):
        """Exclusively enables sculpting or selection."""
        self.plotter.disable_picking() # Disable any active picker
        if enabled:
            self.area_mode_btn.setChecked(False) # Ensure area selection is off
            self.plotter.enable_point_picking(callback=self.handle_click, show_message=False, color="pink")
            self.chat_history.append("<b>System:</b> Sculpt Mode Active. Click to pull the surface.")
        else:
            self.plotter.enable_mesh_picking(callback=self.on_mesh_picked, show=False) # Re-enable default mesh picking

    def update_density(self, value):
        self.density_level = value
        self.chat_history.append(f"<b>System:</b> Geometric density set to level {value}.")

    def init_ai_section(self):
        """UI for talking to the AI and history tracking."""
        ai_group = QtWidgets.QGroupBox("AI Design Assistant")
        ai_layout = QtWidgets.QVBoxLayout()

        # Chat display for AI responses
        self.chat_history = QtWidgets.QTextEdit()
        self.chat_history.setReadOnly(True)
        self.chat_history.setMaximumHeight(150)
        ai_layout.addWidget(self.chat_history)

        # Pulse indicator / Status Label & Save Macro Row
        status_row = QtWidgets.QHBoxLayout()
        self.ai_status_label = QtWidgets.QLabel()
        self.set_ai_status("Ready", "#00d2d3")
        status_row.addWidget(self.ai_status_label)
        
        status_row.addStretch()
        
        self.save_macro_btn = QtWidgets.QPushButton("💾 Save Last Action")
        self.save_macro_btn.setToolTip("Save the last successful AI action as a macro")
        self.save_macro_btn.setEnabled(False)
        self.save_macro_btn.clicked.connect(self.save_last_action_macro)
        self.save_macro_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 2px 6px;
                font-size: 10px;
            }
            QPushButton:disabled {
                background-color: #7f8c8d;
                color: #bdc3c7;
            }
            QPushButton:hover:enabled {
                background-color: #2ecc71;
            }
        """)
        status_row.addWidget(self.save_macro_btn)
        
        ai_layout.addLayout(status_row)

        # Interaction area
        input_layout = QtWidgets.QHBoxLayout()
        self.ai_input = QtWidgets.QLineEdit()
        self.ai_input.setPlaceholderText("Tell the AI to modify your design (e.g., 'Make it 50mm tall and wider')...")
        self.ai_input.returnPressed.connect(self.process_ai_command)
        
        # Setup advanced autocomplete on self.ai_input
        self.ai_suggestions = [
            "Create a procedural table",
            "Create a procedural chair",
            "Create a procedural staircase",
            "Create a procedural house",
            "Create a procedural gear",
            "Create a procedural mug",
            "Create a procedural vase",
            "Create a custom helix spring",
            "Create a closed torus knot",
            "Create a custom 3D star",
            "Create a custom 3D heart stand",
            "Create a Möbius strip",
            "Create a Klein bottle representation",
            "Create a Lorenz chaos attractor ribbon",
            "Create a Sierpinski fractal pyramid",
            "Create a gyroid infill periodic structure",
            "Apply polished gold shader",
            "Apply liquid chrome shader",
            "Apply holographic neon shader",
            "Apply frosted glass shader",
            "Apply clay shader",
            "Twist the selected shape by 45 degrees",
            "Taper the selected shape by factor 0.5",
            "Bend the selected shape by 45 degrees",
            "Stretch the selected shape on Z axis by factor 1.5",
            "Bulge the selected shape by factor 0.3",
            "Smooth the selected shape using Laplacian filter",
            "Subdivide the selected shape's density",
            "Smart duplicate the selected part",
            "Drop the selected shape to the bed",
            "Align all parts along the X axis",
            "Perform subtract boolean cut",
            "Analyze the scene printability and errors",
            "Clear current selection",
            "Reset all creative sliders",
        ]
        completer = QtWidgets.QCompleter(self.ai_suggestions, self.central_widget)
        completer.setCaseSensitivity(QtCore.Qt.CaseSensitivity.CaseInsensitive)
        completer.setFilterMode(QtCore.Qt.MatchFlag.MatchContains)
        self.ai_input.setCompleter(completer)

        # Voice Button
        self.voice_btn = QtWidgets.QPushButton("🎤 Talk to AI") # Define voice_btn here
        self.voice_btn.setToolTip("Click to speak your design requirements") # Set tooltip
        self.voice_btn.clicked.connect(self.toggle_voice) # Connect to toggle_voice
        
        # Settings button
        self.ai_settings_btn = QtWidgets.QPushButton("⚙")
        self.ai_settings_btn.setToolTip("Configure Offline AI Quality and Subdivision Settings")
        self.ai_settings_btn.setFixedWidth(30)
        self.ai_settings_btn.clicked.connect(self.open_ai_settings_dialog)
        
        input_layout.addWidget(self.ai_input)
        input_layout.addWidget(self.voice_btn)
        input_layout.addWidget(self.ai_settings_btn)
        ai_layout.addLayout(input_layout)

        # Quick Action Chips for intuitive clicks
        chips_layout = QtWidgets.QHBoxLayout()
        chips_layout.addWidget(QtWidgets.QLabel("Try:"))
        
        chips = [
            ("📐 Table", "Create a procedural table at the center"),
            ("🪑 Chair", "Create a procedural chair at the center"),
            ("🔍 Analyze", "Analyze the scene printability and errors"),
            ("🌀 Twist", "Twist selected shape by 45 degrees"),
            ("💎 Chrome", "Apply the liquid chrome shader to the selected shape"),
            ("🌟 Align Bed", "Align bottom of selected shape to touch Z=0 build plate"),
            ("🧬 DNA", "Spawn a double helix DNA strand"),
        ]
        
        for text, prompt in chips:
            btn = QtWidgets.QPushButton(text)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #2c3e50;
                    color: #ecf0f1;
                    border: 1px solid #7f8c8d;
                    border-radius: 8px;
                    padding: 2px 6px;
                    font-size: 10px;
                }
                QPushButton:hover {
                    background-color: #34495e;
                    border-color: #00d2d3;
                    color: #00d2d3;
                }
            """)
            btn.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
            btn.clicked.connect(self.make_chip_callback(prompt))
            chips_layout.addWidget(btn)
        
        chips_layout.addStretch()
        ai_layout.addLayout(chips_layout)

        ai_group.setLayout(ai_layout)
        self.layout.addWidget(ai_group)

    @QtCore.pyqtSlot(str, str)
    def set_ai_status(self, status_text, color):
        self.ai_status_label.setText(f"<b>AI Status:</b> <span style='color: {color}; font-weight: bold;'>{status_text}</span>")

    def make_chip_callback(self, prompt):
        def _callback():
            self.ai_input.setText(prompt)
            self.process_ai_command()
        return _callback

    def init_macro_panel(self):
        """Creates the UI panel for saved AI Macros."""
        layout = self.macro_tab_layout
        
        group = QtWidgets.QGroupBox("Custom AI Macros")
        g_layout = QtWidgets.QVBoxLayout(group)
        
        self.macro_list = QtWidgets.QListWidget()
        self.macro_list.itemClicked.connect(self.display_macro_code)
        g_layout.addWidget(self.macro_list)
        
        # Code Preview
        g_layout.addWidget(QtWidgets.QLabel("Macro Python Code:"))
        self.macro_code_preview = QtWidgets.QTextEdit()
        self.macro_code_preview.setReadOnly(True)
        self.macro_code_preview.setStyleSheet("background-color: #1e272e; color: #2ecc71; font-family: monospace; font-size: 10px;")
        g_layout.addWidget(self.macro_code_preview)
        
        btn_layout = QtWidgets.QHBoxLayout()
        run_btn = QtWidgets.QPushButton("▶ Run Macro")
        run_btn.setStyleSheet("background-color: #27ae60; color: white;")
        run_btn.clicked.connect(self.run_selected_macro)
        
        del_btn = QtWidgets.QPushButton("🗑 Delete")
        del_btn.setStyleSheet("background-color: #c0392b; color: white;")
        del_btn.clicked.connect(self.delete_selected_macro)
        
        btn_layout.addWidget(run_btn)
        btn_layout.addWidget(del_btn)
        g_layout.addLayout(btn_layout)
        
        layout.addWidget(group)

    def load_macros(self):
        """Loads macros from ai_macros.json."""
        macro_file = os.path.join(log_dir, "ai_macros.json")
        if os.path.exists(macro_file):
            try:
                import json
                with open(macro_file, "r", encoding="utf-8") as f:
                    self.custom_macros = json.load(f)
            except Exception as e:
                print(f"Failed to load macros: {e}")
        QtCore.QTimer.singleShot(500, self.refresh_macro_buttons)
        
    def refresh_macro_buttons(self):
        """Populates the macro list widget."""
        if hasattr(self, 'macro_list'):
            self.macro_list.clear()
            self.macro_list.addItems(self.custom_macros.keys())
            
    def display_macro_code(self, item):
        """Displays the python code of the clicked macro."""
        name = item.text()
        if name in self.custom_macros:
            self.macro_code_preview.setPlainText(self.custom_macros[name])
            
    def run_selected_macro(self):
        """Runs the selected macro script on the main thread."""
        item = self.macro_list.currentItem()
        if not item: return
        name = item.text()
        code_str = self.custom_macros.get(name)
        if code_str:
            self.chat_history.append(f"<b>System:</b> Running macro '{name}'...")
            self._execute_ai_code(code_str, f"Run macro {name}")
            
    def delete_selected_macro(self):
        """Deletes the selected macro."""
        item = self.macro_list.currentItem()
        if not item: return
        name = item.text()
        if name in self.custom_macros:
            del self.custom_macros[name]
            macro_file = os.path.join(log_dir, "ai_macros.json")
            try:
                import json
                with open(macro_file, "w", encoding="utf-8") as f:
                    json.dump(self.custom_macros, f, indent=4)
            except Exception as e:
                print(f"Failed to save macros: {e}")
            self.refresh_macro_buttons()
            self.macro_code_preview.clear()
            self.chat_history.append(f"<b>System:</b> Macro '{name}' deleted.")
            
    def save_last_action_macro(self):
        """Saves the last executed AI python script as a macro."""
        if not self.last_executed_code: return
        name, ok = QtWidgets.QInputDialog.getText(self, "Save Macro", "Enter macro name (e.g. 'Build Helix Stand'):")
        if ok and name:
            self.custom_macros[name] = self.last_executed_code
            macro_file = os.path.join(log_dir, "ai_macros.json")
            try:
                import json
                with open(macro_file, "w", encoding="utf-8") as f:
                    json.dump(self.custom_macros, f, indent=4)
            except Exception as e:
                print(f"Failed to save macro: {e}")
            self.refresh_macro_buttons()
            self.chat_history.append(f"<b>System:</b> Saved macro '{name}'! You can run it from the AI Macros tab.")

    def open_ai_settings_dialog(self):
        """Opens a dialog to configure Local Offline AI parameters (Subdivision Density, Marching Cubes grid resolution)."""
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("Offline AI Configuration")
        dialog.resize(350, 180)
        
        layout = QtWidgets.QVBoxLayout(dialog)
        
        grid = QtWidgets.QGridLayout()
        grid.addWidget(QtWidgets.QLabel("Mesh Subdivision Density:"), 0, 0)
        density_combo = QtWidgets.QComboBox()
        density_combo.addItems([str(i) for i in range(5)])
        density_combo.setCurrentText(str(self.density_level))
        grid.addWidget(density_combo, 0, 1)
        
        grid.addWidget(QtWidgets.QLabel("Implicit Grid Resolution:"), 1, 0)
        grid_combo = QtWidgets.QComboBox()
        grid_combo.addItems(["15 (Fast)", "25 (Medium)", "40 (High Q)", "60 (Extreme)"])
        # Select active grid resolution
        cur_res = getattr(self, 'grid_resolution', 25)
        if cur_res == 15:
            grid_combo.setCurrentText("15 (Fast)")
        elif cur_res == 25:
            grid_combo.setCurrentText("25 (Medium)")
        elif cur_res == 40:
            grid_combo.setCurrentText("40 (High Q)")
        elif cur_res == 60:
            grid_combo.setCurrentText("60 (Extreme)")
        grid.addWidget(grid_combo, 1, 1)
        
        layout.addLayout(grid)
        
        info_lbl = QtWidgets.QLabel("<i>Tip: Higher density and resolution levels create smoother mathematical curves and gyroid meshes, but require more processing time.</i>")
        info_lbl.setWordWrap(True)
        info_lbl.setStyleSheet("font-size: 10px; color: gray;")
        layout.addWidget(info_lbl)
        
        btn_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.StandardButton.Ok | QtWidgets.QDialogButtonBox.StandardButton.Cancel)
        btn_box.accepted.connect(dialog.accept)
        btn_box.rejected.connect(dialog.reject)
        layout.addWidget(btn_box)
        
        if dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            self.density_level = int(density_combo.currentText())
            grid_text = grid_combo.currentText()
            if "15" in grid_text:
                self.grid_resolution = 15
            elif "25" in grid_text:
                self.grid_resolution = 25
            elif "40" in grid_text:
                self.grid_resolution = 40
            elif "60" in grid_text:
                self.grid_resolution = 60
            self.chat_history.append(f"<b>System:</b> Offline AI reconfigured. Density Level={self.density_level}, Grid Resolution={self.grid_resolution}.")

    def analyze_scene(self):
        """Performs a 3D printability, collision, and alignment inspection on the current scene."""
        if not self.meshes:
            msg = "No meshes in scene to analyze. Create some shapes first!"
            self.chat_history.append(f"<b>AI Analyst:</b> {msg}")
            self.speak(msg)
            return

        self.chat_history.append("<b>AI Analyst:</b> Running printability checks and collision inspection...")
        
        total_vol = 0.0
        collision_count = 0
        floating_count = 0
        oob_count = 0
        overhang_count = 0
        
        part_reports = []
        L_X, L_Y, L_Z = self.BUILD_LIMITS
        mesh_names = list(self.meshes.keys())
        
        for i in range(len(mesh_names)):
            for j in range(i + 1, len(mesh_names)):
                m1 = self.meshes[mesh_names[i]]
                m2 = self.meshes[mesh_names[j]]
                b1 = m1.bounds
                b2 = m2.bounds
                overlap = not (b1[1][0] < b2[0][0] or b1[0][0] > b2[1][0] or
                              b1[1][1] < b2[0][1] or b1[0][1] > b2[1][1] or
                              b1[1][2] < b2[0][2] or b1[0][2] > b2[1][2])
                if overlap:
                    collision_count += 1

        for name, mesh in self.meshes.items():
            vol_cm3 = mesh.volume / 1000.0
            total_vol += vol_cm3
            
            b = mesh.bounds
            out_of_bounds = False
            if b[0][0] < -L_X/2 or b[1][0] > L_X/2 or b[0][1] < -L_Y/2 or b[1][1] > L_Y/2 or b[0][2] < 0 or b[1][2] > L_Z:
                out_of_bounds = True
                oob_count += 1
                
            z_min = b[0][2]
            floating = z_min > 0.5
            if floating:
                floating_count += 1
                
            steep_faces = np.sum(mesh.face_normals[:, 2] < -0.707)
            if steep_faces > 0:
                overhang_count += 1
                
            part_reports.append(
                f"<tr>"
                f"<td>{name}</td>"
                f"<td>{vol_cm3:.2f} cm³</td>"
                f"<td style='color: {'red' if out_of_bounds else 'green'};'>{'Exceeded' if out_of_bounds else 'OK'}</td>"
                f"<td style='color: {'red' if floating else 'green'};'>{'Floating' if floating else 'On Bed'}</td>"
                f"<td>{steep_faces} faces</td>"
                f"</tr>"
            )
            
        weight_g = total_vol * 1.24
        est_time_mins = 30 + (total_vol * 8)
        hours = int(est_time_mins // 60)
        mins = int(est_time_mins % 60)
        
        report_html = f"""
        <table border='1' cellpadding='4' style='border-collapse: collapse; width: 100%; font-size: 11px; background-color: #2c3e50; color: white;'>
            <tr style='background-color: #34495e; font-weight: bold;'>
                <th>Part Name</th>
                <th>Volume</th>
                <th>Volume Limit</th>
                <th>Bed Contact</th>
                <th>Overhangs</th>
            </tr>
            {"".join(part_reports)}
        </table>
        <div style='font-size: 11px; margin-top: 6px;'>
            <b>⚡ Est. Weight:</b> {weight_g:.1f}g (PLA)<br>
            <b>⏰ Est. Time:</b> {hours}h {mins}m<br>
            <b>💥 Intersecting Parts:</b> <span style='color: {'red' if collision_count > 0 else 'green'};'>{collision_count} detected</span><br>
            <b>🚨 Critical Alerts:</b> 
            {"None" if (floating_count + oob_count + collision_count) == 0 else 
             f"<span style='color: red;'>{floating_count} floating, {oob_count} out-of-bounds!</span>"}
        </div>
        """
        
        self.chat_history.append(report_html)
        
        if floating_count > 0 or oob_count > 0 or collision_count > 0:
            self.speak("Warning: Bounding alerts or floating parts detected. Review the report.")
        else:
            self.speak("Scene is print-ready. No critical alerts found.")

    def speak(self, text):
        """Converts AI text response to speech in a background thread."""
        # Strip HTML tags for clean speech
        clean_text = re.sub(r'<[^>]*>', '', text)
        def _run():
            try:
                import pyttsx3
                engine = pyttsx3.init()
                engine.say(clean_text)
                engine.runAndWait()
            except: pass
        threading.Thread(target=_run, daemon=True).start()

    # --- 3D Geometry Manipulation ---

    def center_all_meshes(self):
        """Centers the entire collection of meshes on the build plate (0, 0)."""
        if not self.meshes: return
        for name, mesh in self.meshes.items():
            # Center X and Y, keep Z on floor
            translation = [-mesh.centroid[0], -mesh.centroid[1], -mesh.bounds[0][2]]
            mesh.apply_translation(translation)
        self.update_canvas()
        self.chat_history.append("<b>System:</b> All models centered on AD5X build plate.")

    def save_project(self):
        """Saves the entire scene state to a project file."""
        path, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save Project", "", "3D Designer Project (*.3dp)")
        if path:
            try:
                # Store mesh data as dictionaries for serialization
                data = {name: {'vertices': m.vertices, 'faces': m.faces} for name, m in self.meshes.items()}
                with open(path, 'wb') as f:
                    pickle.dump(data, f)
                self.chat_history.append(f"<b>System:</b> Project saved to {path}")
            except Exception as e:
                self.chat_history.append(f"<b>Error:</b> Save failed: {str(e)}")

    def load_project(self):
        """Loads a previously saved project file."""
        path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Open Project", "", "3D Designer Project (*.3dp)")
        if path:
            try:
                with open(path, 'rb') as f:
                    data = pickle.load(f)
                self.meshes.clear()
                for name, m_data in data.items():
                    self.meshes[name] = trimesh.Trimesh(vertices=m_data['vertices'], faces=m_data['faces'])
                self.update_canvas()
                self.chat_history.append(f"<b>System:</b> Project {os.path.basename(path)} loaded.")
            except Exception as e:
                self.chat_history.append(f"<b>Error:</b> Load failed: {str(e)}")

    def import_3d_model(self):
        """
        Opens a file dialog to allow the user to select and import a 3D model file.
        Supports common formats like STL, OBJ, PLY, GLTF, 3MF.
        """
        file_dialog = QtWidgets.QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(
            self, "Import 3D Model", "", 
            "3D Model Files (*.stl *.obj *.ply *.gltf *.glb *.3mf);;All Files (*)"
        )

        if file_path:
            try:
                loaded = trimesh.load(file_path)
                # If it's a Scene (multi-part model), concatenate to form a single solid mesh
                if isinstance(loaded, trimesh.Scene):
                    mesh = loaded.dump(concatenate=True)
                else:
                    mesh = loaded
                # Snap bottom of mesh to build plate
                mesh.apply_translation([0, 0, -mesh.bounds[0][2]])
                name = f"Imported_{mesh.metadata.get('file_name', 'Model')}_{len(self.meshes)}"
                self.meshes[name] = mesh
                self.selected_mesh_name = name
                self.reset_creative_sliders()
                self.update_canvas()
                msg = f"Successfully imported {file_path.split('/')[-1]}."
                self.chat_history.append(f"<b>System:</b> {msg}")
                self.speak(msg)
            except Exception as e:
                self.chat_history.append(f"<b>Error:</b> Failed to import model: {str(e)}")

    def import_photos_to_3d(self):
        """
        Allows user to select multiple photos. 
        In a production environment, these would be uploaded to a Cloud AI service.
        """
        file_dialog = QtWidgets.QFileDialog()
        files, _ = file_dialog.getOpenFileNames(
            self, "Select 4 Photos of Object (Front, Back, Left, Right)", 
            "", "Images (*.png *.jpg *.jpeg)"
        )

        if len(files) >= 1:
            self.chat_history.append(f"<b>System:</b> Received {len(files)} photos.")
            
            # Intelligent Feedback Logic for 3D Reconstruction
            if len(files) < 4:
                self.chat_history.append("<b>AI:</b> Coverage is too low. <b>Need more angles from the back</b> and sides to avoid 'hollow' spots.")
            elif 4 <= len(files) < 8:
                self.chat_history.append("<b>AI:</b> Getting closer. I have the front and sides, but I need <b>high-angle (top-down)</b> shots to finish the head and shoulders.")
            else:
                self.chat_history.append("<b>AI:</b> 360-degree coverage detected. Excellent detail for a figurine.")
            
            self.chat_history.append("<b>AI:</b> Analyzing features and reconstructing point cloud...")
            # Simulation of AI generation delay
            QtCore.QTimer.singleShot(2000, lambda: self.chat_history.append("<b>AI:</b> Meshing vertices and generating manifold surface..."))
            QtCore.QTimer.singleShot(4000, lambda: self.chat_history.append("<b>System:</b> 3D Object generated. (Connect an API key to Meshy/Luma for real results)"))
            # For now, we drop a sphere as a placeholder for the reconstructed object
            self.add_primitive("Sphere")

    def remove_background_ai(self):
        """
        Allows user to select an image for background removal.
        In a production environment, this would be uploaded to a Cloud AI service.
        """
        file_dialog = QtWidgets.QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(
            self, "Select Image for Background Removal", 
            "", "Images (*.png *.jpg *.jpeg)"
        )

        if file_path:
            self.chat_history.append(f"<b>System:</b> Received image: {file_path.split('/')[-1]}.")
            self.chat_history.append("<b>AI:</b> Analyzing image for foreground and background elements...")
            # Simulate AI processing delay
            QtCore.QTimer.singleShot(2000, lambda: self.chat_history.append("<b>AI:</b> Background successfully removed! (Connect an API key to remove.bg or ClipDrop for real results)"))
            # In a real scenario, the processed image (e.g., PNG with transparency) would be returned here.
            # For now, we just confirm the action.

    def add_primitive(self, shape_type):
        """Adds a new shape to the scene."""
        name = f"{shape_type}_{len(self.meshes)}"
        if shape_type == "Cube":
            mesh = trimesh.creation.box(extents=[40, 40, 40]) # Standardized start size
        elif shape_type == "Sphere":
            mesh = trimesh.creation.icosphere(radius=20)
        elif shape_type == "Cylinder":
            mesh = trimesh.creation.cylinder(radius=20, height=40)
        elif shape_type == "Cone":
            mesh = trimesh.creation.cone(radius=20, height=40)
        elif shape_type == "Pyramid":
            mesh = trimesh.creation.cone(radius=20, height=40, sections=4)
        elif shape_type == "Torus":
            mesh = trimesh.creation.torus(major_radius=20, minor_radius=5)
        elif shape_type == "Capsule":
            mesh = trimesh.creation.capsule(radius=10, height=40)
        elif shape_type == "Annulus":
            mesh = trimesh.creation.annulus(inner_radius=10, outer_radius=20, height=10)
        elif shape_type == "Helix":
            mesh = self.generate_procedural_helix()
        elif shape_type == "Torus Knot":
            mesh = self.generate_procedural_torus_knot()
        elif shape_type == "Star":
            mesh = self.generate_procedural_star()
        elif shape_type == "Heart":
            mesh = self.generate_procedural_heart()
        elif shape_type == "Hex Prism":
            mesh = trimesh.creation.cylinder(radius=20, height=40, sections=6)
        elif shape_type == "Oct Prism":
            mesh = trimesh.creation.cylinder(radius=20, height=40, sections=8)
        elif shape_type == "Bolt":
            self.create_bolt(8); return
        elif shape_type == "Nut":
            self.create_nut(8); return
        elif shape_type == "Peg":
            self.create_peg(8); return
        elif shape_type == "Sketch Mode":
            self.chat_history.append("System: Sketch Mode enabled. Use your mouse to define points.")
            return

        # Default Texture Check
        default_pat = self.default_tex_combo.currentText()

        # Apply density and default pattern
        for _ in range(self.density_level):
            vertices, faces = trimesh.remesh.subdivide(mesh.vertices, mesh.faces)
            mesh = trimesh.Trimesh(vertices=vertices, faces=faces)
            
        if default_pat != "None":
            mesh.vertices += self.pattern_functions[default_pat](mesh.vertices)

        # Snap bottom to Z=0
        mesh.apply_translation([0, 0, -mesh.bounds[0][2]])

        self.meshes[name] = mesh
        self.selected_mesh_name = name
        self.reset_creative_sliders()
        self.update_canvas()

    def add_bolt_dialog(self):
        """Prompt user for bolt size."""
        sizes = [f"{i}mm" for i in [1, 2, 3, 4, 5, 6, 8, 10, 12, 16, 20]]
        size_str, ok = QtWidgets.QInputDialog.getItem(self, "Bolt Selection", "Select Diameter:", sizes, 3, False)
        if ok:
            size = int("".join(filter(str.isdigit, size_str)))
            self.create_bolt(size)

    def add_bolt_with_hole_dialog(self):
        """Adds a bolt and carves a matching hole in the selected mesh."""
        if not self.selected_mesh_name:
            self.chat_history.append("<b>System:</b> Please select a shape first to seat the bolt into.")
            return
        sizes = [f"{i}mm" for i in [1, 2, 3, 4, 5, 6, 8, 10, 12, 16, 20]]
        size_str, ok = QtWidgets.QInputDialog.getItem(self, "Integrated Bolt Selection", "Select Size:", sizes, 3, False)
        if ok:
            size = int("".join(filter(str.isdigit, size_str)))
            self.create_bolt_with_hole(size)

    def add_peg_dialog(self):
        """Prompt user for peg size."""
        sizes = [f"{i}mm" for i in [2, 3, 4, 5, 6, 8, 10, 12]]
        size_str, ok = QtWidgets.QInputDialog.getItem(self, "Peg Selection", "Select Diameter:", sizes, 3, False)
        if ok:
            size = int("".join(filter(str.isdigit, size_str)))
            self.create_peg(size)

    def add_peg_with_hole_dialog(self):
        """Adds a peg and carves a matching hole in the selected mesh."""
        if not self.selected_mesh_name:
            self.chat_history.append("<b>System:</b> Select a shape first to seat the peg into.")
            return
        sizes = [f"{i}mm" for i in [2, 3, 4, 5, 6, 8, 10, 12]]
        size_str, ok = QtWidgets.QInputDialog.getItem(self, "Integrated Peg Selection", "Select Diameter:", sizes, 3, False)
        if ok:
            size = int("".join(filter(str.isdigit, size_str)))
            self.create_peg_with_hole(size)

    def create_peg(self, size):
        """Generates a parametric dowel peg."""
        self.save_state()
        name = f"Peg_D{size}_{len(self.meshes)}"
        mesh = trimesh.creation.cylinder(radius=size/2, height=size*3)
        mesh.apply_translation([0, 0, -mesh.bounds[0][2]])
        self.meshes[name] = mesh
        self.selected_mesh_name = name
        self.update_canvas()
        self.chat_history.append(f"<b>System:</b> Added M{size} dowel peg.")

    def create_peg_with_hole(self, size):
        """Generates a peg and subtracts a matching hole from the selected part."""
        self.save_state()
        parent_name = self.selected_mesh_name
        parent_mesh = self.meshes[parent_name]
        
        name = f"Peg_D{size}_{len(self.meshes)}"
        radius = size / 2
        height = size * 3
        peg_mesh = trimesh.creation.cylinder(radius=radius, height=height)
        
        # Create drill with 0.2mm tolerance for press-fit
        drill = trimesh.creation.cylinder(radius=radius + 0.2, height=height + 10)
        
        try:
            self.meshes[parent_name] = trimesh.boolean.difference([parent_mesh, drill])
            self.meshes[name] = peg_mesh
            self.update_canvas()
            self.chat_history.append(f"<b>System:</b> Integrated M{size} peg and matching hole into {parent_name}.")
        except Exception as e:
            self.chat_history.append(f"<b>Error:</b> Failed to carve peg hole: {str(e)}")

    def add_drawer_dialog(self):
        """Prompt user for drawer parameters to ensure a perfect mechanical fit."""
        if not self.selected_mesh_name:
            self.chat_history.append("<b>System:</b> Select a box to convert into a cabinet.")
            return
        wall, ok1 = QtWidgets.QInputDialog.getDouble(self, "Drawer Design", "Shell Thickness (mm):", 2.0, 1.0, 10.0)
        if not ok1: return
        clear, ok2 = QtWidgets.QInputDialog.getDouble(self, "Drawer Design", "Clearance/Tolerance (mm):", 0.4, 0.1, 5.0)
        if ok2:
            self.create_drawer_in_box(wall, clear)

    def create_drawer_in_box(self, wall, clearance):
        """Carves a cavity into the selected box and generates a matching drawer object."""
        self.save_state()
        base_name = self.selected_mesh_name
        base_mesh = self.meshes[base_name]
        ext = base_mesh.extents
        center = base_mesh.centroid

        try:
            # 1. Create Cavity (Hole in the box)
            # We ensure the cavity breaks through the front (+Y) face cleanly
            cav_ext = [ext[0] - 2*wall, ext[1], ext[2] - 2*wall]
            cavity = trimesh.creation.box(extents=cav_ext)
            cavity.apply_translation(center + [0, wall/2, 0])
            self.meshes[base_name] = trimesh.boolean.difference([base_mesh, cavity])

            # 2. Create Drawer Shell
            drw_ext = [cav_ext[0] - 2*clearance, ext[1] - wall, cav_ext[2] - 2*clearance]
            drawer_shell = trimesh.creation.box(extents=drw_ext)
            
            # 3. Hollow out the drawer
            inner_ext = [drw_ext[0] - 2*wall, drw_ext[1], drw_ext[2] - wall]
            inner_vol = trimesh.creation.box(extents=inner_ext)
            inner_vol.apply_translation([0, wall/2, wall/2])
            drawer = trimesh.boolean.difference([drawer_shell, inner_vol])

            # 4. Add a handle (small bridge)
            handle = trimesh.creation.box(extents=[drw_ext[0]/3, 4, 8])
            handle.apply_translation([0, drw_ext[1]/2 + 2, 0])
            drawer = trimesh.util.concatenate([drawer, handle])

            drawer.apply_translation(center + [0, wall/2, 0])
            name = f"Drawer_for_{base_name}"
            self.meshes[name] = drawer
            self.update_canvas()
            self.chat_history.append(f"<b>System:</b> Integrated drawer and cabinet generated.")
        except Exception as e:
            self.chat_history.append(f"<b>Error:</b> Boolean operation failed: {str(e)}")

    def create_bolt_with_hole(self, size):
        """Generates a bolt and subtracts a matching hole from the active part."""
        parent_name = self.selected_mesh_name
        parent_mesh = self.meshes[parent_name]
        
        # 1. Create the Bolt (Visual Part)
        bolt_name = f"Bolt_M{size}_{len(self.meshes)}"
        shaft_h = size * 5
        shaft = trimesh.creation.cylinder(radius=size/2, height=shaft_h)
        shaft.apply_translation([0, 0, shaft_h/2])
        head_h = size * 0.8
        head = trimesh.creation.cylinder(radius=size * 0.9, height=head_h, sections=6)
        head.apply_translation([0, 0, shaft_h + head_h/2])
        bolt_mesh = trimesh.util.concatenate([shaft, head])
        
        # 2. Create the 'Drill' tool (slightly larger for tolerance)
        drill = trimesh.creation.cylinder(radius=(size/2) + 0.3, height=shaft_h * 2)
        drill.apply_translation([0, 0, shaft_h]) # Align with bolt shaft
        
        try:
            # 3. Carve the hole into the parent part
            self.meshes[parent_name] = trimesh.boolean.difference([parent_mesh, drill])
            # 4. Add the bolt as its own object
            self.meshes[bolt_name] = bolt_mesh
            self.update_canvas()
            self.chat_history.append(f"<b>System:</b> Integrated M{size} bolt and matching hole into {parent_name}.")
        except Exception as e:
            self.chat_history.append(f"<b>Error:</b> Could not carve hole. {str(e)}")

    def add_nut_dialog(self):
        """Prompt user for nut size."""
        sizes = [f"{i}mm" for i in [1, 2, 3, 4, 5, 6, 8, 10, 12, 16, 20]]
        size_str, ok = QtWidgets.QInputDialog.getItem(self, "Nut Selection", "Select Diameter (to match bolt):", sizes, 3, False)
        if ok:
            size = int("".join(filter(str.isdigit, size_str)))
            self.create_nut(size)

    def create_nut(self, size):
        """Generates a parametric nut with 3D print tolerances for sturdiness."""
        name = f"Nut_M{size}_{len(self.meshes)}"
        # High density design: wide walls for mechanical strength
        outer_radius = size * 0.9 
        height = size * 0.8
        
        # Create the hex body
        nut_body = trimesh.creation.cylinder(radius=outer_radius, height=height, sections=6)
        
        # Create the hole with a 0.3mm tolerance offset for 3D printing
        hole_radius = (size / 2) + 0.3
        hole = trimesh.creation.cylinder(radius=hole_radius, height=height + 2)
        
        # Boolean subtraction to create the nut
        mesh = trimesh.boolean.difference([nut_body, hole])
        mesh.apply_translation([0, 0, -mesh.bounds[0][2]])
        self.meshes[name] = mesh
        self.selected_mesh_name = name
        self.update_canvas()
        self.chat_history.append(f"<b>System:</b> Added M{size} reinforced nut (with 0.3mm tolerance).")

    def create_bolt(self, size):
        """Generates a parametric hex-head bolt based on mm size."""
        name = f"Bolt_M{size}_{len(self.meshes)}"
        shaft_h = size * 5
        shaft = trimesh.creation.cylinder(radius=size/2, height=shaft_h)
        shaft.apply_translation([0, 0, shaft_h/2])
        
        head_h = size * 0.8
        head = trimesh.creation.cylinder(radius=size * 0.9, height=head_h, sections=6)
        head.apply_translation([0, 0, shaft_h + head_h/2])
        
        mesh = trimesh.util.concatenate([shaft, head])
        mesh.apply_translation([0, 0, -mesh.bounds[0][2]])
        self.meshes[name] = mesh
        self.selected_mesh_name = name
        self.update_canvas()
        self.chat_history.append(f"<b>System:</b> Added M{size} parametric bolt.")

    def add_hinge(self, style):
        """Generates mechanical hinge mechanisms."""
        name = f"Hinge_{style}_{len(self.meshes)}"
        if style == "Barrel":
            p1 = trimesh.creation.cylinder(radius=4, height=12)
            p2 = trimesh.creation.cylinder(radius=4, height=12)
            p1.apply_translation([0, 0, 6])
            p2.apply_translation([0, 0, 19])
            mesh = trimesh.util.concatenate([p1, p2])
        else: # Leaf Style
            w, d, h = 25, 2, 25
            l1, l2 = trimesh.creation.box(extents=[w, d, h]), trimesh.creation.box(extents=[w, d, h])
            pin = trimesh.creation.cylinder(radius=2, height=h)
            pin.apply_transform(trimesh.transformations.rotation_matrix(np.pi/2, [1, 0, 0]))
            l1.apply_translation([w/2, d/2, 0]); l2.apply_translation([-w/2, d/2, 0])
            mesh = trimesh.util.concatenate([l1, l2, pin])
            
        mesh.apply_translation([0, 0, -mesh.bounds[0][2]])
        self.meshes[name] = mesh
        self.selected_mesh_name = name
        self.update_canvas()
        self.chat_history.append(f"<b>System:</b> Added {style} style hinge.")

    def merge_all_meshes(self):
        """Fuses all shapes into a single watertight mesh (Boolean Union)."""
        if len(self.meshes) < 2:
            self.chat_history.append("<b>System:</b> Need at least two shapes to merge.")
            return
            
        try:
            combined = trimesh.boolean.union(list(self.meshes.values()))
            self.meshes = {"Merged_Model": combined}
            self.selected_mesh_name = "Merged_Model"
            self.reset_creative_sliders()
            self.update_canvas()
            self.chat_history.append("<b>System:</b> All parts merged into a single solid body.")
        except Exception as e:
            self.chat_history.append(f"<b>Error:</b> Could not merge. Ensure shapes overlap. {str(e)}")

    def duplicate_selected(self):
        """Copies the selected mesh and offsets it slightly."""
        if not self.selected_mesh_name:
            return
        
        original = self.meshes[self.selected_mesh_name]
        new_mesh = original.copy()
        
        # Smart Duplicate: Use the last known translation offset
        new_mesh.apply_translation(self.last_duplicate_offset)
        
        new_name = f"{self.selected_mesh_name}_Copy_{len(self.meshes)}"
        self.meshes[new_name] = new_mesh
        self.selected_mesh_name = new_name
        self.reset_creative_sliders()
        self.update_canvas()
        self.chat_history.append(f"<b>System:</b> Duplicated {new_name}.")

    def align_selected_dialog(self):
        """Tinkercad-style alignment for multiple parts."""
        selected_items = self.object_list.selectedItems()
        if len(selected_items) < 2:
            self.chat_history.append("<b>System:</b> Select at least 2 parts in the list to align them.")
            return
            
        axes = ["X-Axis", "Y-Axis", "Z-Axis (Floor)"]
        axis_str, ok = QtWidgets.QInputDialog.getItem(self, "Alignment", "Align along:", axes, 0, False)
        if not ok: return
        
        axis_idx = axes.index(axis_str)
        
        # Calculate the collective center of all selected items
        target_meshes = [self.meshes[item.text()] for item in selected_items]
        if axis_str == "Z-Axis (Floor)":
            # Special logic: Drop the bottom of every selected mesh to Z=0
            for mesh in target_meshes:
                z_min = mesh.bounds[0][2]
                mesh.apply_translation([0, 0, -z_min])
        else:
            centers = [m.centroid[axis_idx] for m in target_meshes]
            mean_center = sum(centers) / len(centers)
            for mesh in target_meshes:
                offset = np.zeros(3)
                offset[axis_idx] = mean_center - mesh.centroid[axis_idx]
                mesh.apply_translation(offset)
            
        self.update_canvas()
        self.chat_history.append(f"<b>System:</b> Aligned {len(selected_items)} parts to common {axis_str} center.")

    def subtract_logic(self, base_name=None, tool_name=None):
        """Uses the selected mesh as a 'hole' to cut into another mesh."""
        if len(self.meshes) < 2:
            self.chat_history.append("<b>System:</b> Need at least two shapes to perform subtraction.")
            return

        if base_name and tool_name:
            if base_name in self.meshes and tool_name in self.meshes:
                ok = True
            else:
                ok = False
        else:
            if not self.selected_mesh_name:
                self.chat_history.append("<b>System:</b> Select the 'Hole' shape, and ensure there is another shape to cut into.")
                return
            tool_name = self.selected_mesh_name
            other_meshes = [name for name in self.meshes.keys() if name != tool_name]
            base_name, ok = QtWidgets.QInputDialog.getItem(self, "Subtractive Modeling", "Select Base Shape to cut into:", other_meshes, 0, False)

        if ok and base_name and tool_name:
            try:
                base_mesh = self.meshes[base_name]
                hole_mesh = self.meshes[tool_name]
                
                # Perform boolean subtraction
                new_base = trimesh.boolean.difference([base_mesh, hole_mesh])
                self.meshes[base_name] = new_base
                if tool_name in self.meshes:
                    del self.meshes[tool_name]
                self.selected_mesh_name = base_name
                self.update_canvas()
                self.chat_history.append(f"<b>System:</b> Successfully carved {tool_name} into {base_name}.")
            except Exception as e:
                self.chat_history.append(f"<b>Error:</b> Boolean subtraction failed. {str(e)}")

    def union_logic(self, base_name=None, tool_name=None):
        """Combines two shapes using boolean union offline."""
        if len(self.meshes) < 2:
            self.chat_history.append("<b>System:</b> Need at least two shapes to merge.")
            return

        if base_name and tool_name:
            if base_name in self.meshes and tool_name in self.meshes:
                ok = True
            else:
                ok = False
        else:
            if not self.selected_mesh_name:
                self.chat_history.append("<b>System:</b> Select a shape, and ensure there is another shape to merge it with.")
                return
            tool_name = self.selected_mesh_name
            other_meshes = [name for name in self.meshes.keys() if name != tool_name]
            base_name, ok = QtWidgets.QInputDialog.getItem(self, "Additive Modeling", "Select shape to merge with:", other_meshes, 0, False)

        if ok and base_name and tool_name:
            try:
                base_mesh = self.meshes[base_name]
                tool_mesh = self.meshes[tool_name]
                new_base = trimesh.boolean.union([base_mesh, tool_mesh])
                self.meshes[base_name] = new_base
                if tool_name in self.meshes:
                    del self.meshes[tool_name]
                self.selected_mesh_name = base_name
                self.update_canvas()
                self.chat_history.append(f"<b>System:</b> Successfully merged {tool_name} and {base_name}.")
            except Exception as e:
                self.chat_history.append(f"<b>Error:</b> Boolean union failed. {str(e)}")

    def intersection_logic(self, base_name=None, tool_name=None):
        """Finds intersection of two shapes offline."""
        if len(self.meshes) < 2:
            self.chat_history.append("<b>System:</b> Need at least two shapes to intersect.")
            return

        if base_name and tool_name:
            if base_name in self.meshes and tool_name in self.meshes:
                ok = True
            else:
                ok = False
        else:
            if not self.selected_mesh_name:
                self.chat_history.append("<b>System:</b> Select a shape, and ensure there is another shape to intersect it with.")
                return
            tool_name = self.selected_mesh_name
            other_meshes = [name for name in self.meshes.keys() if name != tool_name]
            base_name, ok = QtWidgets.QInputDialog.getItem(self, "Intersect Modeling", "Select shape to intersect with:", other_meshes, 0, False)

        if ok and base_name and tool_name:
            try:
                base_mesh = self.meshes[base_name]
                tool_mesh = self.meshes[tool_name]
                new_base = trimesh.boolean.intersection([base_mesh, tool_mesh])
                self.meshes[base_name] = new_base
                if tool_name in self.meshes:
                    del self.meshes[tool_name]
                self.selected_mesh_name = base_name
                self.update_canvas()
                self.chat_history.append(f"<b>System:</b> Successfully intersected {tool_name} and {base_name}.")
            except Exception as e:
                self.chat_history.append(f"<b>Error:</b> Intersection failed. {str(e)}")

    def update_canvas(self):
        """Refreshes the 3D view with current geometry."""
        # Avoid self.plotter.clear() to keep interactive state and widgets stable
        self.draw_build_plate() 
        
        # Surgical removal of deleted actors
        existing_actors = list(self.plotter.renderer.actors.keys())
        for actor_name in existing_actors:
            if actor_name not in self.meshes and actor_name not in ["build_plate", "axes"]:
                self.plotter.remove_actor(actor_name)
        
        # Sync the object list
        self.object_list.blockSignals(True)
        self.object_list.clear()
        for name, mesh in self.meshes.items():
            list_item = QtWidgets.QListWidgetItem(name)
            self.object_list.addItem(list_item)

            if name == self.selected_mesh_name:
                list_item.setSelected(True)

            pv_mesh = pv.wrap(mesh)

            # Add or update mesh actor by name to preserve picking observers
            if hasattr(mesh.visual, 'vertex_colors') and len(mesh.visual.vertex_colors) > 0:
                self.plotter.add_mesh(
                    pv_mesh, 
                    scalars=mesh.visual.vertex_colors[:, :3], 
                    rgb=True, 
                    show_edges=True, 
                    line_width=2,
                    name=name,
                    pickable=True
                )
            else:
                color = "#00F0FF" if name == self.selected_mesh_name else "white"
                self.plotter.add_mesh(pv_mesh, name=name, color=color, show_edges=True, line_width=2, pickable=True)

        self.object_list.blockSignals(False)
        self.apply_aesthetic_shader(self.current_aesthetic_style)
        self.plotter.render()
        self.refresh_widgets()

    def get_active_mesh(self, default_shape="Cube"):
        """Returns the selected mesh name. If the scene is empty or no selection is valid, creates a default shape."""
        if not self.meshes:
            self.add_primitive(default_shape)
        elif not self.selected_mesh_name or self.selected_mesh_name not in self.meshes:
            self.selected_mesh_name = list(self.meshes.keys())[-1]
        return self.selected_mesh_name

    def process_ai_command(self):
        """Parses the text input to manipulate the 3D shapes using the local offline AI."""
        command = self.ai_input.text().lower().strip()
        if not command: return
        self.chat_history.append(f"<b>You:</b> {command}")
        self.ai_input.clear()

        # Intercept printability check and scene analysis
        if any(kw in command for kw in ["analyze", "check print", "printability", "inspect", "scene report"]):
            self.analyze_scene()
            return

        # Save to chat history for conversational memory
        self.ai_chat_history.append({"role": "User", "content": command})
        self.process_basic_command(command)

    def generate_complex_procedural_mesh(self, prompt):
        """Simple clean fallback to generate primitive shapes when offline."""
        import trimesh
        import numpy as np
        
        # Simple compound shape as fallback
        body = trimesh.creation.icosphere(radius=12)
        base = trimesh.creation.box(extents=[16, 16, 6])
        base.apply_translation([0, 0, -12])
        return trimesh.util.concatenate([body, base])

    def generate_3d_from_text(self, prompt):
        """Handles complex organic generation requests using Gemini AI synthesis."""
        self.chat_history.append(f"<b>AI:</b> Initiating Neural Mesh Synthesis for: '{prompt}'...")
        self.speak(f"Analyzing form and structure for {prompt}. Synthesizing complex geometry.")
        
        # Start background thread for synthesis
        self.synthesis_thread = GeminiSynthesisThread(prompt, parent=self)
        self.synthesis_thread.start()

    def _handle_synthesis_success(self, prompt, mesh, code):
        try:
            mesh.apply_translation([0, 0, -mesh.bounds[0][2]])
        except Exception:
            pass
        
        name = f"AI_Generated_{len(self.meshes)}"
        self.meshes[name] = mesh
        self.selected_mesh_name = name
        self.update_canvas()
        self.chat_history.append(f"<b>System:</b> Model '{prompt}' successfully synthesized using Gemini AI.")
        self.speak("Geometry synthesized successfully.")
        
        # Enable the save macro button and store the code in last_executed_code
        self.last_executed_code = code
        self.save_macro_btn.setEnabled(True)

    def _handle_synthesis_error(self, prompt, err_msg, code):
        self.chat_history.append(f"<b>System:</b> Synthesis failed: {err_msg}")
        self.speak("Failed to synthesize geometry.")

    def _log_ai_chat(self, msg):
        self.chat_history.append(msg)

    def _handle_offline_fallback(self, prompt):
        self.chat_history.append("<b>System:</b> Gemini API Key missing or offline. Contacting Offline Procedural Engine...")
        self.speak("Falling back to local templates.")
        try:
            mesh = self.generate_complex_procedural_mesh(prompt)
            mesh.apply_translation([0, 0, -mesh.bounds[0][2]])
            name = f"Offline_Generated_{len(self.meshes)}"
            self.meshes[name] = mesh
            self.selected_mesh_name = name
            self.update_canvas()
            self.chat_history.append(f"<b>System:</b> Local model for '{prompt}' generated as fallback.")
        except Exception as e:
            self.chat_history.append(f"<b>System:</b> Fallback failed: {e}")

    def toggle_voice(self):
        """Enables microphone listening."""
        if self.is_listening: return
        self.is_listening = True
        self.voice_btn.setText("🎤 Listening...")
        threading.Thread(target=self.listen_to_voice, daemon=True).start()

    def listen_to_voice(self):
        try:
            import speech_recognition as sr
            r = sr.Recognizer()
            with sr.Microphone() as source:
                r.adjust_for_ambient_noise(source, duration=0.5)
                audio = r.listen(source, timeout=5)
                text = r.recognize_google(audio)
                QtCore.QMetaObject.invokeMethod(self, "_handle_voice_input", QtCore.Qt.ConnectionType.QueuedConnection, QtCore.Q_ARG(str, text))
        except Exception as e:
            QtCore.QMetaObject.invokeMethod(self, "_handle_voice_error", QtCore.Qt.ConnectionType.QueuedConnection, QtCore.Q_ARG(str, str(e)))

    @QtCore.pyqtSlot(str)
    def _handle_voice_input(self, text):
        self.is_listening = False
        self.voice_btn.setText("🎤 Talk to AI")
        self.ai_input.setText(text)
        self.process_ai_command()

    @QtCore.pyqtSlot(str)
    def _handle_voice_error(self, err):
        self.is_listening = False
        self.voice_btn.setText("🎤 Talk to AI")
        self.chat_history.append(f"<b>System:</b> Voice Error: {err}")

    def process_basic_command(self, command):
        """Original heuristic-based logic for offline use, now with advanced procedural modeling."""
        import offline_ai
        return offline_ai.process_basic_command(self, command)

    # --- Texture & Art Functions ---

    def init_pattern_registry(self):
        """Maps pattern names to logic functions."""
        self.pattern_functions = {
            "Stucco": lambda v: np.random.normal(0, 0.8, v.shape),
            "Ridges": self._ridges_logic,
            "Waves": self._waves_logic,
            "Crumpled": lambda v: np.random.uniform(-2, 2, v.shape),
            "Plaid": self._plaid_logic,
            "Polka": self._dots_logic,
            "Brick": self._brick_logic,
            "Spiral": self._spiral_logic,
            "Honeycomb": self._honeycomb_logic,
            "Diamond": self._diamond_logic,
            "Wood": self._wood_logic,
            "Scales": self._scales_logic,
            "Leather": lambda v: np.random.normal(0, 0.4, v.shape),
            "Carbon": self._carbon_logic,
            "ZigZag": self._zigzag_logic,
            "Knurl": self._knurl_logic,
            "Sand": lambda v: np.random.normal(0, 0.15, v.shape),
            "Grooves": self._grooves_logic,
            "Pebbles": self._pebbles_logic,
            "Voronoi": self._voronoi_logic,
            "Gyroid": self._gyroid_logic,
            "Rectilinear": self._rectilinear_logic,
            "Archimedean": self._archimedean_logic,
            "Octagram": self._octagram_logic,
            "Chevron": self._chevron_logic,
            "Thread": self._thread_logic,
            "Damascus": self._damascus_logic,
            "Lava": self._lava_logic,
            "VoronoiFacets": self._voronoi_facets_logic
        }

    def _ridges_logic(self, v):
        disp = np.zeros_like(v)
        disp[:, 0] = np.sin(v[:, 1] * 0.5) * 2.0
        return disp

    def _waves_logic(self, v):
        disp = np.zeros_like(v)
        disp[:, 2] = (np.sin(v[:, 0] * 0.2) + np.cos(v[:, 1] * 0.2)) * 1.5
        return disp

    def _plaid_logic(self, v):
        disp = np.zeros_like(v)
        freq = 0.5
        disp[:, 2] = (np.abs(np.sin(v[:, 0] * freq)) + np.abs(np.sin(v[:, 1] * freq))) * 1.5
        return disp

    def _dots_logic(self, v):
        disp = np.zeros_like(v)
        pattern = np.sin(v[:, 0] * 0.2) * np.sin(v[:, 1] * 0.2)
        disp[:, 2] = np.where(pattern > 0.7, 2.0, 0)
        return disp

    def _brick_logic(self, v):
        disp = np.zeros_like(v)
        y_brick = np.sin(v[:, 1] * 0.4)
        shift = np.where(y_brick > 0, 0.5, 0)
        x_brick = np.sin((v[:, 0] + shift) * 0.4)
        disp[:, 2] = np.where((y_brick > 0.9) | (x_brick > 0.9), -1.0, 0.5)
        return disp

    def _spiral_logic(self, v):
        disp = np.zeros_like(v)
        r = np.sqrt(v[:, 0]**2 + v[:, 1]**2)
        theta = np.arctan2(v[:, 1], v[:, 0])
        disp[:, 2] = np.sin(r * 0.5 - theta * 2.0) * 2.0
        return disp

    def _honeycomb_logic(self, v):
        disp = np.zeros_like(v)
        freq = 0.4
        h = (np.sin(v[:, 0] * freq) + np.sin(v[:, 0] * freq * 0.5 + v[:, 1] * freq * 0.866) + 
             np.sin(v[:, 0] * freq * 0.5 - v[:, 1] * freq * 0.866))
        disp[:, 2] = np.where(h > 1.5, 1.5, 0)
        return disp

    def _diamond_logic(self, v):
        disp = np.zeros_like(v)
        freq = 0.3
        disp[:, 2] = (np.abs(np.sin(v[:, 0] * freq)) + np.abs(np.sin(v[:, 1] * freq))) * 2.0
        return disp

    def _wood_logic(self, v):
        disp = np.zeros_like(v)
        r = np.sqrt(v[:, 0]**2 + v[:, 1]**2)
        noise = np.random.normal(0, 0.5, len(v))
        disp[:, 2] = np.sin(r * 0.2 + noise) * 0.8
        return disp

    def _scales_logic(self, v):
        disp = np.zeros_like(v)
        freq = 0.4
        pattern = np.sin(v[:, 0] * freq) * np.cos(v[:, 1] * freq)
        disp[:, 2] = np.where(pattern > 0, pattern * 2.0, 0)
        return disp

    def _carbon_logic(self, v):
        disp = np.zeros_like(v)
        disp[:, 2] = np.sin(v[:, 0]*2) * np.sin(v[:, 1]*2) * 0.5
        return disp

    def _zigzag_logic(self, v):
        disp = np.zeros_like(v)
        disp[:, 2] = np.abs((v[:, 0]*0.5) % 1 - 0.5) * 4.0
        return disp

    def _knurl_logic(self, v):
        disp = np.zeros_like(v)
        pattern = np.abs(np.sin(v[:, 0]*1.2)) + np.abs(np.sin(v[:, 1]*1.2))
        disp[:, 2] = np.where(pattern > 1.5, 1.5, 0)
        return disp

    def _grooves_logic(self, v):
        disp = np.zeros_like(v)
        disp[:, 2] = np.where(np.sin(v[:, 0]*1.0) > 0.8, -1.0, 0)
        return disp

    def _pebbles_logic(self, v):
        disp = np.random.normal(0, 0.2, v.shape)
        pattern = np.sin(v[:, 0]*0.3) * np.cos(v[:, 1]*0.3)
        disp[:, 2] += np.where(pattern > 0.6, 2.5, 0)
        return disp

    def _voronoi_logic(self, v):
        # Simulated organic cellular noise
        disp = np.zeros_like(v)
        disp[:, 2] = np.abs(np.sin(v[:, 0]*0.2) * np.cos(v[:, 1]*0.2)) * 3.0
        return disp

    def _gyroid_logic(self, v):
        disp = np.zeros_like(v)
        scale = 0.3
        val = (np.sin(v[:, 0] * scale) * np.cos(v[:, 1] * scale) + 
               np.sin(v[:, 1] * scale) * np.cos(v[:, 2] * scale) + 
               np.sin(v[:, 2] * scale) * np.cos(v[:, 0] * scale))
        disp[:, 2] = val * 2.5
        return disp

    def _rectilinear_logic(self, v):
        disp = np.zeros_like(v)
        freq = 0.4
        pattern = np.maximum(np.abs(np.sin(v[:, 0] * freq)), np.abs(np.sin(v[:, 1] * freq)))
        disp[:, 2] = np.where(pattern > 0.9, 1.5, 0)
        return disp

    def _archimedean_logic(self, v):
        disp = np.zeros_like(v)
        r = np.sqrt(v[:, 0]**2 + v[:, 1]**2)
        disp[:, 2] = np.sin(r * 0.5) * 1.5
        return disp

    def _octagram_logic(self, v):
        disp = np.zeros_like(v)
        freq = 0.2
        pattern = np.sin(v[:, 0] * freq + v[:, 1] * freq) * np.sin(v[:, 0] * freq - v[:, 1] * freq)
        disp[:, 2] = np.where(np.abs(pattern) > 0.6, 2.0, 0)
        return disp

    def _chevron_logic(self, v):
        disp = np.zeros_like(v)
        pattern = np.abs((v[:, 0] + np.abs(v[:, 1])) * 0.3 % 2 - 1.0)
        disp[:, 2] = np.where(pattern > 0.5, 1.5, -1.5)
        return disp

    def _thread_logic(self, v):
        disp = np.zeros_like(v)
        theta = np.arctan2(v[:, 1], v[:, 0])
        z = v[:, 2]
        pitch = 8.0
        pattern = np.sin((z * (2 * np.pi / pitch)) - theta)
        norm = np.linalg.norm(v[:, :2], axis=1, keepdims=True)
        norm = np.where(norm == 0, 1.0, norm)
        disp[:, :2] = (v[:, :2] / norm) * np.where(pattern > 0, 1.5, -0.5)[:, np.newaxis]
        return disp

    def apply_texture_by_name(self, name):
        """Applies a specific texture logic to the mesh."""
        if name in self.pattern_functions:
            self._displace_mesh(self.pattern_functions[name])

    def pick_color(self, index):
        color = QtWidgets.QColorDialog.getColor(self.current_colors[index])
        if color.isValid():
            self.current_colors[index] = color
            btns = [self.c1_btn, self.c2_btn]
            btns[index].setStyleSheet(f"background-color: {color.name()}; height: 30px;")

    def apply_color_bond(self):
        """Merges two colors into a vertical gradient 'bond'."""
        if not self.selected_mesh_name: return
        mesh = self.meshes[self.selected_mesh_name]
        
        # Calculate Z-based gradient
        z = mesh.vertices[:, 2]
        z_min, z_max = z.min(), z.max()
        ratio = (z - z_min) / (z_max - z_min) if z_max > z_min else z * 0
        
        c1 = self.current_colors[0].getRgb()[:3]
        c2 = self.current_colors[1].getRgb()[:3]
        
        colors = np.zeros((len(mesh.vertices), 3), dtype=np.uint8)
        for i in range(3):
            colors[:, i] = (c1[i] * (1 - ratio) + c2[i] * ratio).astype(np.uint8)
        
        mesh.visual.vertex_colors = colors
        self.update_canvas()
        self.chat_history.append("<b>System:</b> Color Bond applied and locked.")

    def _displace_mesh(self, func):
        """Helper to modify vertices and refresh view."""
        if not self.selected_mesh_name: return
        mesh = self.meshes[self.selected_mesh_name]
        
        # Use the density slider to determine how much to subdivide before texturing
        for _ in range(self.density_level):
            vertices, faces = trimesh.remesh.subdivide(mesh.vertices, mesh.faces)
            mesh = trimesh.Trimesh(vertices=vertices, faces=faces)
            
        displacement = func(mesh.vertices)
        
        # Apply masking if "Brush" selection is active
        if self.active_selection_indices is not None:
            mask = np.zeros(len(mesh.vertices), dtype=bool)
            mask[self.active_selection_indices] = True
            mesh.vertices[mask] += displacement[mask]
        else:
            mesh.vertices += displacement
        
        # Re-smooth slightly so it looks 'polished' and not broken
        trimesh.smoothing.filter_laplacian(mesh, iterations=2)
        
        self.meshes[self.selected_mesh_name] = mesh
        self.update_canvas()
        self.chat_history.append("<b>AI:</b> Texture blended and applied to surface.")

    def _damascus_logic(self, v):
        disp = np.zeros_like(v)
        wave = np.sin(v[:, 0] * 0.45) + np.sin(v[:, 1] * 0.45) + np.cos(v[:, 2] * 0.45)
        disp[:, 2] = np.sin(wave * 2.2) * 1.6
        return disp

    def _lava_logic(self, v):
        disp = np.zeros_like(v)
        val = np.sin(v[:, 0] * 0.16) * np.cos(v[:, 1] * 0.16)
        disp[:, 2] = np.where(val > 0.45, 2.6 * (val - 0.45), np.where(val < -0.45, 1.9 * (val + 0.45), 0))
        return disp

    def _voronoi_facets_logic(self, v):
        disp = np.zeros_like(v)
        val = (np.floor(v[:, 0] * 0.12) + np.floor(v[:, 1] * 0.12)) * 0.5
        disp[:, 2] = np.sin(val) * 2.2
        return disp

    def export_to_3mf(self):
        """Combines all current shapes and exports to 3MF format."""
        if not self.meshes:
            return
        
        # Create scene and enforce Flashforge-compatible units
        scene = trimesh.Scene(list(self.meshes.values()))
        scene.units = self.UNIT
        
        file_path, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Export to 3MF", "", "3MF Files (*.3mf)")
        
        if file_path:
            scene.export(file_path, file_type='3mf', digits=6)
            self.chat_history.append(f"<b>System:</b> File successfully saved to {file_path}")

    def export_to_stl(self):
        """Exports the selected mesh or the entire scene to STL."""
        if not self.meshes: return
        file_path, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Export to STL", "", "STL Files (*.stl)")
        if file_path:
            try:
                if self.selected_mesh_name and self.selected_mesh_name in self.meshes:
                    mesh = self.meshes[self.selected_mesh_name]
                else:
                    mesh = trimesh.util.concatenate(list(self.meshes.values()))
                mesh.export(file_path, file_type='stl')
                self.chat_history.append(f"<b>System:</b> STL successfully saved to {file_path}")
            except Exception as e:
                self.chat_history.append(f"<b>Error:</b> STL export failed: {str(e)}")

    def export_to_obj(self):
        """Exports the selected mesh or the entire scene to OBJ."""
        if not self.meshes: return
        file_path, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Export to OBJ", "", "OBJ Files (*.obj)")
        if file_path:
            try:
                if self.selected_mesh_name and self.selected_mesh_name in self.meshes:
                    mesh = self.meshes[self.selected_mesh_name]
                else:
                    mesh = trimesh.util.concatenate(list(self.meshes.values()))
                mesh.export(file_path, file_type='obj')
                self.chat_history.append(f"<b>System:</b> OBJ successfully saved to {file_path}")
            except Exception as e:
                self.chat_history.append(f"<b>Error:</b> OBJ export failed: {str(e)}")

    def generate_procedural_chair(self, *args, **kwargs):
        import offline_ai
        return offline_ai.generate_procedural_chair(self, *args, **kwargs)

    def generate_procedural_table(self, *args, **kwargs):
        import offline_ai
        return offline_ai.generate_procedural_table(self, *args, **kwargs)

    def generate_procedural_staircase(self, *args, **kwargs):
        import offline_ai
        return offline_ai.generate_procedural_staircase(self, *args, **kwargs)

    def generate_procedural_house(self, *args, **kwargs):
        import offline_ai
        return offline_ai.generate_procedural_house(self, *args, **kwargs)

    def generate_procedural_gear(self, *args, **kwargs):
        import offline_ai
        return offline_ai.generate_procedural_gear(self, *args, **kwargs)

    def generate_procedural_mug(self, *args, **kwargs):
        import offline_ai
        return offline_ai.generate_procedural_mug(self, *args, **kwargs)

    def generate_procedural_vase(self, *args, **kwargs):
        import offline_ai
        return offline_ai.generate_procedural_vase(self, *args, **kwargs)

    def apply_cyberpunk_theme(self):
        """Applies a professional, vibrant dark-cyberpunk UI stylesheet to the application."""
        theme = """
        QMainWindow {
            background-color: #121217;
            color: #e0e0e8;
            font-family: 'Segoe UI', 'Outfit', sans-serif;
        }
        QWidget {
            background-color: #121217;
            color: #e0e0e8;
        }
        QGroupBox {
            border: 2px solid #222230;
            border-radius: 8px;
            margin-top: 12px;
            font-weight: bold;
            color: #00f0ff;
            background-color: #161622;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            subcontrol-position: top left;
            left: 8px;
            padding: 0 4px;
        }
        QTabWidget::pane {
            border: 1px solid #222230;
            background-color: #121217;
            border-radius: 4px;
        }
        QTabBar::tab {
            background: #1c1c28;
            border: 1px solid #222230;
            border-bottom-color: none;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
            padding: 6px 12px;
            color: #a0a0b0;
        }
        QTabBar::tab:selected {
            background: #161622;
            color: #00f0ff;
            border-bottom: 2px solid #00f0ff;
            font-weight: bold;
        }
        QPushButton {
            background-color: #1d1d2b;
            border: 1px solid #33334d;
            border-radius: 4px;
            padding: 6px 12px;
            color: #ffffff;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #00f0ff;
            color: #121217;
            border: 1px solid #00f0ff;
        }
        QPushButton:pressed {
            background-color: #ff007f;
            color: #ffffff;
            border: 1px solid #ff007f;
        }
        QLineEdit {
            background-color: #0b0b0f;
            border: 1px solid #222230;
            border-radius: 4px;
            padding: 4px;
            color: #00f0ff;
        }
        QTextEdit {
            background-color: #0b0b0f;
            border: 1px solid #222230;
            border-radius: 4px;
            color: #e0e0e8;
        }
        QListWidget {
            background-color: #0b0b0f;
            border: 1px solid #222230;
            border-radius: 4px;
            color: #e0e0e8;
        }
        QListWidget::item:selected {
            background-color: #ff007f;
            color: #ffffff;
            font-weight: bold;
        }
        QSlider::groove:horizontal {
            border: 1px solid #222230;
            height: 6px;
            background: #0b0b0f;
            border-radius: 3px;
        }
        QSlider::handle:horizontal {
            background: #00f0ff;
            border: 1px solid #00f0ff;
            width: 14px;
            height: 14px;
            margin: -4px 0;
            border-radius: 7px;
        }
        QSlider::handle:horizontal:hover {
            background: #ff007f;
            border: 1px solid #ff007f;
        }
        QDoubleSpinBox {
            background-color: #0b0b0f;
            border: 1px solid #222230;
            border-radius: 4px;
            padding: 2px;
            color: #00f0ff;
        }
        QToolBar {
            background-color: #161622;
            border-bottom: 1px solid #222230;
            spacing: 8px;
            padding: 4px;
        }
        QToolButton {
            background-color: transparent;
            border: 1px solid transparent;
            border-radius: 4px;
            padding: 4px;
            color: #e0e0e8;
            font-weight: bold;
        }
        QToolButton:hover {
            background-color: #1c1c28;
            border: 1px solid #33334d;
            color: #00f0ff;
        }
        QStatusBar {
            background-color: #161622;
            color: #a0a0b0;
            border-top: 1px solid #222230;
        }
        """
        self.setStyleSheet(theme)

    def apply_aesthetic_shader(self, style_name):
        """Applies advanced high-end rendering shaders to all meshes in the scene."""
        self.current_aesthetic_style = style_name
        for name in self.meshes:
            actor = self.plotter.renderer.actors.get(name)
            if not actor: continue
            prop = actor.GetProperty()
            
            # Reset properties to clean state
            prop.SetAmbient(0.1)
            prop.SetDiffuse(0.7)
            prop.SetSpecular(0.2)
            prop.SetOpacity(1.0)
            
            if style_name == "default":
                prop.SetInterpolationToGouraud()
                prop.SetMetallic(0.0)
                prop.SetRoughness(0.5)
                # Highlights selected item
                if name == self.selected_mesh_name:
                    prop.SetColor(0.0, 0.94, 1.0) # Glowing Cyan
                else:
                    prop.SetColor(1.0, 1.0, 1.0) # White
            elif style_name == "gold":
                prop.SetInterpolationToPBR()
                prop.SetMetallic(1.0)
                prop.SetRoughness(0.18)
                prop.SetColor(1.0, 0.84, 0.0) # Gold RGB
            elif style_name == "chrome":
                prop.SetInterpolationToPBR()
                prop.SetMetallic(1.0)
                prop.SetRoughness(0.05)
                prop.SetColor(0.95, 0.95, 0.95) # Mirror Chrome RGB
            elif style_name == "glass":
                prop.SetInterpolationToPBR()
                prop.SetMetallic(0.1)
                prop.SetRoughness(0.1)
                prop.SetOpacity(0.35)
                prop.SetColor(0.0, 0.94, 1.0) # Glass Cyan
            elif style_name == "neon":
                prop.SetInterpolationToFlat()
                prop.SetAmbient(1.0)
                prop.SetDiffuse(0.0)
                prop.SetColor(1.0, 0.0, 0.5) # Neon pink
            elif style_name == "clay":
                prop.SetInterpolationToGouraud()
                prop.SetMetallic(0.0)
                prop.SetRoughness(0.9)
                prop.SetColor(0.8, 0.45, 0.35) # Terracotta clay
        self.plotter.render()

    def add_math_shape(self, shape_type):
        """Generates mathematical art models and updates the active scene."""
        self.save_state()
        self.chat_history.append(f"<b>System:</b> Plotting Mathematical Art structure '{shape_type}'...")
        if shape_type == "mobius":
            mesh = self.create_mobius_strip()
            name = f"Math_Mobius_{len(self.meshes)}"
        elif shape_type == "klein":
            mesh = self.create_klein_bottle()
            name = f"Math_Klein_{len(self.meshes)}"
        elif shape_type == "gyroid":
            mesh = self.create_gyroid_infill()
            name = f"Math_Gyroid_{len(self.meshes)}"
        elif shape_type == "lorenz":
            mesh = self.create_lorenz_attractor()
            name = f"Math_Lorenz_{len(self.meshes)}"
        elif shape_type == "sierpinski":
            mesh = self.create_sierpinski_pyramid()
            name = f"Math_Sierpinski_{len(self.meshes)}"
        elif shape_type == "dna":
            mesh = self.create_dna_helix()
            name = f"Math_DNA_{len(self.meshes)}"
        elif shape_type in ["wave", "ripple"]:
            mesh = self.create_wave_surface()
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

    def create_mobius_strip(self, *args, **kwargs):
        import offline_ai
        return offline_ai.create_mobius_strip(self, *args, **kwargs)

    def create_klein_bottle(self, *args, **kwargs):
        import offline_ai
        return offline_ai.create_klein_bottle(self, *args, **kwargs)

    def create_gyroid_infill(self, *args, **kwargs):
        import offline_ai
        return offline_ai.create_gyroid_infill(self, *args, **kwargs)

    def create_lorenz_attractor(self, *args, **kwargs):
        import offline_ai
        return offline_ai.create_lorenz_attractor(self, *args, **kwargs)

    def create_sierpinski_pyramid(self, *args, **kwargs):
        import offline_ai
        return offline_ai.create_sierpinski_pyramid(self, *args, **kwargs)

    def create_dna_helix(self, *args, **kwargs):
        import offline_ai
        return offline_ai.create_dna_helix(self, *args, **kwargs)

    def create_wave_surface(self, *args, **kwargs):
        import offline_ai
        return offline_ai.create_wave_surface(self, *args, **kwargs)

    def get_shape_base_mesh(self, shape_type):
        import offline_ai
        return offline_ai.get_shape_base_mesh(self, shape_type)

    def apply_embedded_aesthetics(self, command):
        import offline_ai
        return offline_ai.apply_embedded_aesthetics(self, command)

    def generate_procedural_helix(self, *args, **kwargs):
        import offline_ai
        return offline_ai.generate_procedural_helix(self, *args, **kwargs)

    def generate_procedural_torus_knot(self, *args, **kwargs):
        import offline_ai
        return offline_ai.generate_procedural_torus_knot(self, *args, **kwargs)

    def generate_procedural_star(self, *args, **kwargs):
        import offline_ai
        return offline_ai.generate_procedural_star(self, *args, **kwargs)

    def generate_procedural_heart(self, *args, **kwargs):
        import offline_ai
        return offline_ai.generate_procedural_heart(self, *args, **kwargs)

if __name__ == "__main__":
    # Create the Qt Application immediately so we can show the splash screen
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")
    
    # 1. Instantly display the Cyberpunk splash screen with a loading progress bar
    splash = BeautifulSplashScreen()
    splash.show()
    QtWidgets.QApplication.processEvents()
    
    # Enable multiprocessing freeze support
    try:
        import multiprocessing
        multiprocessing.freeze_support()
    except Exception:
        pass
        
    try:
        # 2. Check and install dependencies
        splash.update_status("Analyzing system modules...", 15)
        check_and_install_dependencies(lambda msg: splash.update_status(msg, 25))
        
        # 3. Load heavy modules one-by-one, updating the progress bar status
        splash.update_status("Loading configuration templates...", 35)
        import pickle
        import re
        import threading
        
        splash.update_status("Loading core mathematics...", 50)
        import numpy as np
        
        splash.update_status("Loading geometric engine (trimesh)...", 70)
        import trimesh
        
        splash.update_status("Warming up 3D render pipeline...", 85)
        import pyvista as pv
        from pyvistaqt import QtInteractor
        
        splash.update_status("Initializing Offline AI Brain...", 92)
            
        splash.update_status("Waking CAD workspace user interface...", 98)
        
        # Bind the loaded modules to the module level globals so they are accessible to AI3DModeler class methods
        globals()['np'] = np
        globals()['trimesh'] = trimesh
        globals()['pv'] = pv
        globals()['QtInteractor'] = QtInteractor
        globals()['pickle'] = pickle
        globals()['re'] = re
        globals()['threading'] = threading
        globals()['multiprocessing'] = multiprocessing
        
        # Build and present the main window
        window = AI3DModeler()
        splash.update_status("CAD Core Online!", 100)
        
        window.show()
        splash.finish(window)
        sys.exit(app.exec())
    except Exception as e:
        traceback.print_exc()
        QtWidgets.QMessageBox.critical(None, "CAD Engine Startup Error", 
                                       f"The 3D Modeler failed to initialize:\n\n{str(e)}\n\n"
                                       "Please check 'error_log.txt' for the complete traceback.")
        sys.exit(1)
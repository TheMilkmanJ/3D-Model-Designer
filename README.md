# 🧊 AI-Assisted 3D Builder & Designer

Welcome to the ultimate **3D Model Designer**! This application combines a high-detail PyVista canvas, a rich trimesh geometry engine, dynamic deformation filters, PBR aesthetic material shaders, mathematical art generators, and an advanced AI Design Brain powered by Google Gemini to provide a CAD modeling experience.

---

## 🚀 1. Quick Start

### Installation & System Compatibility
Ensure you have Python 3.10+ installed. The application will automatically check for and install missing dependencies on startup. 
*Note: We use standard `trimesh` (instead of `trimesh[all]`) to prevent long compiler/dependency loops and guarantee instant startup.*

To install them manually:
```bash
pip install numpy scipy trimesh pyvista pyvistaqt PyQt6 trame tbb lxml requests google-generativeai SpeechRecognition pyttsx3 pyaudio scikit-image
```

### Launching the Application
Run the designer from your terminal:
```bash
# Optional: Set your Gemini API key in the environment to activate the AI automatically
export GEMINI_API_KEY="your-api-key-here"

python 3D_Model_Designer.py
```

### ⚡ Instant Cyberpunk Splash Loader & Deferred Imports
To resolve traditional PyQt/VTK windowing lag where the system feels frozen or fails to open for 15+ seconds, the application initializes **instantly**:
* **Instant Graphical Feedback**: The GUI runtime immediately creates the Qt app and displays a frameless Cyberpunk styling splash screen (`QSplashScreen`) with a dynamic progress bar within **100 milliseconds**.
* **Deferred Import Loading**: Heavy CAD dependencies (`numpy`, `trimesh`, `pyvista`, `pyvistaqt`) are loaded incrementally in the background, updating the loading progress bar with statuses like *Loading core mathematics*, *Warming up 3D render pipeline*, etc.
* **Error Diagnosis Hook (`error_log.txt`)**: If any crash occurs during this boot sequence (such as missing OpenGL drivers or windowing display failures), a dialog warning box will appear, and the full exception stack trace is written to a local `error_log.txt` file in the folder.

---

## 🎨 2. How to Use Creative Mode

The **Creative Mode** panel unlocks real-time geometric resizing, organic reshaping, and advanced solid modifiers.

### Step-by-Step Workflow:
1. **Activate Creative Mode**: Open the **Creative Mode** tab in the right sidebar and check the **🔓 Enable Creative Mode** box. This unlocks the sliders and buttons.
2. **Select a Shape**: Click on any shape in the 3D viewport or select it in the **Parts Manager** list widget. 
   - *Note: Changing selection automatically resets the sliders back to their neutral positions to prevent compounding transformations.*
3. **Resize Shapes**: 
   - Check **Lock Axes** for uniform proportional scaling.
   - Use the **Scale X**, **Scale Y**, and **Scale Z** sliders to stretch or squeeze shapes.
4. **Reshape Geometry (Deformers)**:
   - **Twist**: Rotates vertices around the Z-axis proportional to their height (spiral/screw effect).
   - **Taper**: Linearly widens or narrows the shape's top.
   - **Bend**: Bends the shape along a smooth curve relative to its center.
   - **Bulge / Swell**: Expands or shrinks the midsection of the shape horizontally.
   - **Organic Noise (Ruffles)**: Adds procedural sinusoidal waves along vertex normals.
   - **Laplacian Smoothing**: Diffuses sharp angles and wrinkles to yield polished, organic surfaces.
5. **Commit the Shape**: Letting go of any slider automatically commits the relative adjustments, resets the sliders to neutral defaults, and saves the state to the **Undo/Redo** stack.

---

## ✨ 3. PBR Aesthetic Shaders & Cyberpunk UI Theme

To make this the coolest modeler ever, we have styled the entire GUI with a **Vibrant Dark-Cyberpunk theme** (neon cyan and magenta highlights) and added advanced Physically-Based Rendering (PBR) shaders.

Go to the **👁 View -> ✨ Aesthetic Styles** menu to apply:
- **🏆 Polished Gold**: Highly reflective, PBR golden finish.
- **💿 Liquid Chrome**: Sleek mirror-chrome metal reflection.
- **💎 Frosted Glass (X-Ray)**: Translucent cyan glass texture with high specular highlights.
- **🔴 Holographic Neon**: Flat shader with ambient self-emission and deep pink/magenta color.
- **🏺 Sculptor Clay**: Terracotta matte clay finish with high surface roughness.
- **✨ Default Material**: Clean CAD material with glowing cyan selection outlines.

---

## 📐 4. Mathematical Art Shapes & Custom Primitives

Add gorgeous mathematical art structures and custom shapes directly into your scene:
* **Custom Geometric Shapes**: Click **🧊 Create** to add:
  - **Helix / Spring**: A parametric, watertight helical spring coil with custom thickness and spacing.
  - **Torus Knot**: A beautiful, continuous figure-8 trefoil knot.
  - **Star**: A solid 3D 5-point star shape.
  - **Heart**: A parametric 3D heart stand.
  - **Hex Prism / Oct Prism**: Clean 6-sided and 8-sided solid CAD prisms.
* **Math Art Shapes**: Select **Create -> Math Art Shapes**:
  - **Möbius Strip**: A single-sided, half-twisted ribbon.
  - **Klein Bottle**: A representation of the non-orientable figure-8 Klein bottle immersion.
  - **Gyroid Infill**: A periodic minimal surface structure (uses Marching Cubes).
  - **Chaos Attractor Ribbon**: A continuous 3D ribbon tracing the chaotic Lorenz differential equation system.
  - **Sierpinski Fractal Pyramid**: A recursive 3D fractal tetrahedron structure.

## 🧠 5. Advanced Context-Aware AI Design Brain

The Gemini-powered AI Design Brain has been heavily upgraded to make design interactions **incredibly smooth and intuitive**:

* **💬 Conversational Memory (Multi-Turn Chat)**: The AI is now context-aware! It remembers your previous requests in the chat. You can converse naturally:
  - *You:* "Create a star at the center"
  - *AI:* (Creates star)
  - *You:* "Make it liquid chrome"
  - *AI:* (Updates shader)
  - *You:* "Now twist it by 45 degrees"
  - *AI:* (Twists the chrome star)
* **⚡ Quick Action Chips**: Below the chat input, you will find small suggestion buttons for common operations ("📐 Table", "🪑 Chair", "🌀 Twist", "💎 Chrome", "🌟 Align Bed", "🔑 Setup API"). Clicking any chip automatically prepares and executes the command instantly.
* **🧠 AI Status Indicator**: A live indicator shows the AI's current neural state:
  - <span style="color: #00d2d3; font-weight: bold;">Ready</span>: Idle and waiting for commands.
  - <span style="color: magenta; font-weight: bold;">Thinking... 🧠</span>: Querying Gemini in a background thread.
  - <span style="color: #f39c12; font-weight: bold;">Debugging... 🛠️</span>: Analyzing code exceptions and auto-correcting geometry.
* **⌨️ Smart Command Autocomplete**: As you type in the AI prompt box, an advanced dropdown filters over 35+ professional CAD, styling, and deformation commands instantly.
* **⚙️ AI Parameter Selector**: Next to the input field, a settings gear button lets you select your active model (`gemini-2.5-flash`, `gemini-2.5-pro`, `gemini-1.5-flash`, `gemini-1.5-pro`) and set custom Temperature/Creativity metrics.
* **💾 Custom AI Macros**: Register successful design commands and scripts into permanent macro buttons! Saving a macro populates a custom GUI panel under the new **AI Macros** tab, permitting one-click replays of your custom designs (persisted locally in `ai_macros.json`).
* **🔍 Printability Copilot (Scene Analysis)**: Type "analyze" or click the `🔍 Analyze` chip to generate a detailed visual HTML report in the chat panel inspecting:
  - Total volume (cm³) and PLA plastic weight (grams).
  - estimated print time.
  - Collisions/intersections between parts.
  - Bed contact alerts (floating parts that would cause print failures).
  - Out of bounds dimensions (pieces exceeding the 220x220x220 build box).
  - Overhang angles (>45 degrees) that require structural support.
* **Real-Time Self-Debugging Loop**: If a generated CAD script encounters a trimesh exception or syntax error, the traceback is captured, Gemini is request-prompted to correct it, and the patched code is seamlessly evaluated on the fly.

### Offline/Heuristic Capabilities:
If no API key is configured, the offline AI still parses basic shapes and procedural assemblies like table, chair, house, vase, mug, gear, and helix springs directly, and performs the local Printability Copilot analysis.

---

## 🛠️ 6. Visual 3D Viewport Controls

Take advantage of professional-grade interactive handles for direct screen manipulation:
* **Advanced Affine Gizmo**: Toggle `Advanced Gizmo` on the toolbar. Click and drag the arrow/ring handles directly on screen to translate or rotate the selected part.
* **Resize Box Handles**: Toggle `Resize Box` on the toolbar. Drag the box vertex handles to scale the shape visually.
* **Shift + Left Click Drag**: Perform direct drag actions on the grid.
* **Ghost Mode**: Toggle semi-transparency to look through walls and inspect internal alignments.
* **Stable Pose (Drop to Bed)**: Auto-rotates parts so their most stable face lies flat on the build plate ($Z=0$), preventing print failures.

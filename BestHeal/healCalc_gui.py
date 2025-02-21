import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

def maxroll_curve(value, factor):
    return value / (value + factor)

def calculate_heal(base_min_damage, base_max_damage, skill_heal, sdb, hac, crit, trials=10000):
    # Compute effective multipliers using maxroll returns
    effective_sdb = maxroll_curve(sdb, 3000)
    effective_crit = maxroll_curve(crit, 6000)
    effective_hac = maxroll_curve(hac, 1000)
    
    # Compute skill damage range
    min_skill_damage = (base_min_damage * 6.1) + 232
    max_skill_damage = (base_max_damage * 6.1) + 232
    
    # Compute healing range
    min_heal = min_skill_damage * (1 + effective_sdb) * (1 + skill_heal)
    max_heal = max_skill_damage * (1 + effective_sdb) * (1 + skill_heal)
    
    # Compute probabilities
    crit_prob = effective_crit
    hac_prob = effective_hac
    
    # Monte Carlo Simulation
    heal_values = []
    crit_count = 0
    hac_count = 0
    crit_hac_count = 0
    
    for _ in range(trials):
        heal = np.random.uniform(min_heal, max_heal)
        is_crit = np.random.rand() < crit_prob
        is_hac = np.random.rand() < hac_prob
        
        if is_crit:
            heal = max_heal  # Crit ensures max heal
            crit_count += 1
        if is_hac:
            heal *= 2  # Heavy Attack doubles heal
            hac_count += 1
        if is_crit and is_hac:
            crit_hac_count += 1
        
        heal_values.append(heal)
    
    return {
        "avg_heal": np.mean(heal_values),
        "min_heal": min_heal,
        "max_heal": max_heal,
        "percentiles": np.percentile(heal_values, [5, 50, 95]),
        "sdb_maxroll": effective_sdb,
        "crit_maxroll": effective_crit,
        "hac_maxroll": effective_hac,
        "crit_percentage": (crit_count / trials) * 100,
        "hac_percentage": (hac_count / trials) * 100,
        "crit_hac_percentage": (crit_hac_count / trials) * 100,
        "distribution": heal_values,
        "sdb": sdb,
        "hac": hac,
        "crit": crit,
        "trials": trials
    }

def analyze_stat_effectiveness(base_min_damage, base_max_damage, skill_heal, sdb, hac, crit, stat_to_analyze, range_points=20, trials=10000):
    """Analyze how effective adding more of a stat would be from current value"""
    results = []
    current_stats = {"sdb": sdb, "hac": hac, "crit": crit}
    
    # Define ranges based on which stat we're analyzing
    if stat_to_analyze == "sdb":
        # Analyze -300 to +300 from current SDB
        stat_range = np.linspace(max(0, sdb - 300), sdb + 300, range_points)
    elif stat_to_analyze == "hac":
        # Analyze -300 to +300 from current HAC
        stat_range = np.linspace(max(0, hac - 300), hac + 300, range_points)
    elif stat_to_analyze == "crit":
        # Analyze -300 to +300 from current crit
        stat_range = np.linspace(max(0, crit - 300), crit + 300, range_points)
    
    # Calculate healing for each value in the range
    for value in stat_range:
        temp_stats = current_stats.copy()
        temp_stats[stat_to_analyze] = value
        
        result = calculate_heal(
            base_min_damage, 
            base_max_damage, 
            skill_heal, 
            temp_stats["sdb"], 
            temp_stats["hac"], 
            temp_stats["crit"],
            trials
        )
        
        results.append({
            "value": value,
            "avg_heal": result["avg_heal"],
            f"{stat_to_analyze}_maxroll": result[f"{stat_to_analyze}_maxroll"]
        })
    
    return results

class HealCalcApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Throne & Liberty Healer Calculator")
        self.root.geometry("1000x800")
        self.root.resizable(True, True)
        
        # Set style
        self.style = ttk.Style()
        self.style.configure("TFrame", background="#f0f0f0")
        self.style.configure("TLabel", background="#f0f0f0", font=("Arial", 10))
        self.style.configure("TButton", font=("Arial", 10))
        self.style.configure("Header.TLabel", font=("Arial", 12, "bold"))
        self.style.configure("Result.TLabel", font=("Arial", 10, "bold"))
        self.style.configure("Documentation.TLabel", font=("Arial", 9))
        
        # Main notebook for tabs
        self.main_notebook = ttk.Notebook(self.root)
        self.main_notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Calculator tab
        self.calculator_frame = ttk.Frame(self.main_notebook, padding="10")
        self.main_notebook.add(self.calculator_frame, text="Calculator")
        
        # Documentation tab
        self.docs_frame = ttk.Frame(self.main_notebook, padding="10")
        self.main_notebook.add(self.docs_frame, text="Documentation")
        
        # Set up calculator UI
        self.setup_calculator_ui()
        
        # Set up documentation UI
        self.setup_documentation_ui()
    
    def setup_calculator_ui(self):
        # Main frame for calculator
        self.main_frame = ttk.Frame(self.calculator_frame)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create base stats frame
        self.create_base_stats_frame()
        
        # Create simulation settings frame
        self.create_simulation_settings_frame()
        
        # Create rune comparison frame
        self.create_rune_comparison_frame()
        
        # Create results frame
        self.create_results_frame()
        
        # Create graph frame
        self.create_graph_frame()
    
    def create_base_stats_frame(self):
        # Base Stats Frame
        base_frame = ttk.LabelFrame(self.main_frame, text="Base Character Stats", padding="10")
        base_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Base stats inputs
        ttk.Label(base_frame, text="Base Min Damage:").grid(column=0, row=0, sticky=tk.W, padx=5, pady=2)
        self.base_min_damage_var = tk.StringVar(value="0")
        ttk.Entry(base_frame, width=10, textvariable=self.base_min_damage_var).grid(column=1, row=0, sticky=tk.W, padx=5, pady=2)
        
        ttk.Label(base_frame, text="Base Max Damage:").grid(column=0, row=1, sticky=tk.W, padx=5, pady=2)
        self.base_max_damage_var = tk.StringVar(value="0")
        ttk.Entry(base_frame, width=10, textvariable=self.base_max_damage_var).grid(column=1, row=1, sticky=tk.W, padx=5, pady=2)
        
        ttk.Label(base_frame, text="Skill Heal (%):").grid(column=2, row=0, sticky=tk.W, padx=5, pady=2)
        self.skill_heal_var = tk.StringVar(value="0.00")
        ttk.Entry(base_frame, width=10, textvariable=self.skill_heal_var).grid(column=3, row=0, sticky=tk.W, padx=5, pady=2)
        
        ttk.Label(base_frame, text="Skill Damage Boost:").grid(column=2, row=1, sticky=tk.W, padx=5, pady=2)
        self.sdb_var = tk.StringVar(value="0")
        ttk.Entry(base_frame, width=10, textvariable=self.sdb_var).grid(column=3, row=1, sticky=tk.W, padx=5, pady=2)
        
        ttk.Label(base_frame, text="Heavy Attack Chance:").grid(column=4, row=0, sticky=tk.W, padx=5, pady=2)
        self.hac_var = tk.StringVar(value="0")
        ttk.Entry(base_frame, width=10, textvariable=self.hac_var).grid(column=5, row=0, sticky=tk.W, padx=5, pady=2)
        
        ttk.Label(base_frame, text="Crit Chance:").grid(column=4, row=1, sticky=tk.W, padx=5, pady=2)
        self.crit_var = tk.StringVar(value="0")
        ttk.Entry(base_frame, width=10, textvariable=self.crit_var).grid(column=5, row=1, sticky=tk.W, padx=5, pady=2)
    
    def create_simulation_settings_frame(self):
        # Simulation Settings Frame
        sim_frame = ttk.LabelFrame(self.main_frame, text="Simulation Settings", padding="10")
        sim_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Trial count slider
        ttk.Label(sim_frame, text="Monte Carlo Trials:").grid(column=0, row=0, sticky=tk.W, padx=5, pady=2)
        
        self.trials_var = tk.IntVar(value=10000)
        self.trials_scale = ttk.Scale(
            sim_frame, 
            from_=1000, 
            to=100000, 
            orient="horizontal", 
            variable=self.trials_var,
            length=300
        )
        self.trials_scale.grid(column=1, row=0, padx=5, pady=2, sticky=tk.W)
        
        # Display the current value
        self.trials_display = ttk.Label(sim_frame, text="10,000")
        self.trials_display.grid(column=2, row=0, padx=5, pady=2)
        
        # Update the display when value changes
        self.trials_scale.configure(command=self.update_trials_display)
        
        # Custom trials entry
        ttk.Label(sim_frame, text="Custom Trials:").grid(column=0, row=1, sticky=tk.W, padx=5, pady=2)
        self.custom_trials_var = tk.StringVar(value="10000")
        custom_trials_entry = ttk.Entry(sim_frame, width=10, textvariable=self.custom_trials_var)
        custom_trials_entry.grid(column=1, row=1, sticky=tk.W, padx=5, pady=2)
        
        # Apply button
        apply_button = ttk.Button(sim_frame, text="Apply Custom", command=self.apply_custom_trials)
        apply_button.grid(column=2, row=1, padx=5, pady=2)
        
        # Warning text
        warning_text = "Warning: Values above 100,000 may significantly slow down calculations"
        ttk.Label(sim_frame, text=warning_text, foreground="red").grid(
            column=0, row=2, columnspan=3, sticky=tk.W, padx=5, pady=2
        )
        
        # Performance hint
        perf_text = "Recommended: 10,000 trials (balance of accuracy and speed)"
        ttk.Label(sim_frame, text=perf_text, foreground="blue").grid(
            column=0, row=3, columnspan=3, sticky=tk.W, padx=5, pady=2
        )
    
    def update_trials_display(self, value):
        """Update the trials display label"""
        trials = int(float(value))
        self.trials_display.configure(text=f"{trials:,}")
        self.custom_trials_var.set(str(trials))
    
    def apply_custom_trials(self):
        """Apply custom trials value"""
        try:
            trials = int(self.custom_trials_var.get())
            if trials < 1000:
                messagebox.showwarning("Warning", "Minimum 1,000 trials recommended for accurate results")
                trials = 1000
            elif trials > 500000:
                result = messagebox.askyesno(
                    "Performance Warning", 
                    "Running more than 500,000 trials may cause your computer to freeze or crash. Continue anyway?"
                )
                if not result:
                    return
            
            self.trials_var.set(min(trials, 100000) if trials <= 100000 else 100000)
            self.trials_display.configure(text=f"{trials:,}")
            
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number")
    
    def create_rune_comparison_frame(self):
        # Rune Comparison Frame
        rune_frame = ttk.LabelFrame(self.main_frame, text="Rune Comparison", padding="10")
        rune_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Rune type selection and value inputs
        self.rune_frames = []
        self.rune_enabled_vars = []
        self.rune_type_vars = []
        self.rune_value_vars = []
        self.rune_names = []
        
        # Column headers
        ttk.Label(rune_frame, text="Enable", style="Header.TLabel").grid(column=0, row=0, padx=5, pady=2)
        ttk.Label(rune_frame, text="Rune Type", style="Header.TLabel").grid(column=1, row=0, padx=5, pady=2)
        ttk.Label(rune_frame, text="Value", style="Header.TLabel").grid(column=2, row=0, padx=5, pady=2)
        ttk.Label(rune_frame, text="Custom Name", style="Header.TLabel").grid(column=3, row=0, padx=5, pady=2)
        
        for i in range(4):
            # Enable checkbox
            rune_enabled_var = tk.BooleanVar(value=True if i == 0 else False)
            self.rune_enabled_vars.append(rune_enabled_var)
            ttk.Checkbutton(rune_frame, variable=rune_enabled_var).grid(column=0, row=i+1, padx=5, pady=2)
            
            # Rune type dropdown
            rune_type_var = tk.StringVar(value="Skill Damage Boost" if i == 0 else "")
            self.rune_type_vars.append(rune_type_var)
            rune_types = ["Skill Damage Boost", "Heavy Attack Chance", "Crit Chance", "Skill Heal"]
            ttk.Combobox(rune_frame, textvariable=rune_type_var, values=rune_types, width=20).grid(column=1, row=i+1, padx=5, pady=2)
            
            # Rune value entry
            rune_value_var = tk.StringVar(value="30" if i == 0 else "")
            self.rune_value_vars.append(rune_value_var)
            ttk.Entry(rune_frame, width=10, textvariable=rune_value_var).grid(column=2, row=i+1, padx=5, pady=2)
            
            # Custom name entry
            rune_name_var = tk.StringVar(value=f"Rune {i+1}" if i == 0 else "")
            self.rune_names.append(rune_name_var)
            ttk.Entry(rune_frame, width=20, textvariable=rune_name_var).grid(column=3, row=i+1, padx=5, pady=2)
        
        # Calculate button
        self.calculate_button = ttk.Button(rune_frame, text="Calculate", command=self.calculate_comparison)
        self.calculate_button.grid(column=0, row=5, columnspan=4, pady=10)
    
    def create_results_frame(self):
        # Results Frame
        self.results_frame = ttk.LabelFrame(self.main_frame, text="Results", padding="10")
        self.results_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create a frame for the results text
        self.results_text_frame = ttk.Frame(self.results_frame)
        self.results_text_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Results Text
        self.results_text = tk.Text(self.results_text_frame, wrap=tk.WORD, width=50, height=20)
        self.results_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Scrollbar for results
        scrollbar = ttk.Scrollbar(self.results_text_frame, orient="vertical", command=self.results_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.results_text.configure(yscrollcommand=scrollbar.set)
    
    def create_graph_frame(self):
        # Graph Frame
        self.graph_frame = ttk.Frame(self.results_frame)
        self.graph_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)
        
        # Graph tabs
        self.graph_notebook = ttk.Notebook(self.graph_frame)
        self.graph_notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create tab for each stat effectiveness curve
        self.sdb_frame = ttk.Frame(self.graph_notebook)
        self.hac_frame = ttk.Frame(self.graph_notebook)
        self.crit_frame = ttk.Frame(self.graph_notebook)
        
        self.graph_notebook.add(self.sdb_frame, text="SDB Effectiveness")
        self.graph_notebook.add(self.hac_frame, text="HAC Effectiveness")
        self.graph_notebook.add(self.crit_frame, text="Crit Effectiveness")
        
        # Create figure for each tab
        self.sdb_figure = Figure(figsize=(5, 4), dpi=100)
        self.sdb_canvas = FigureCanvasTkAgg(self.sdb_figure, master=self.sdb_frame)
        self.sdb_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        self.hac_figure = Figure(figsize=(5, 4), dpi=100)
        self.hac_canvas = FigureCanvasTkAgg(self.hac_figure, master=self.hac_frame)
        self.hac_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        self.crit_figure = Figure(figsize=(5, 4), dpi=100)
        self.crit_canvas = FigureCanvasTkAgg(self.crit_figure, master=self.crit_frame)
        self.crit_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def setup_documentation_ui(self):
        """Set up the documentation tab with explanation of calculations and formulas"""
        # Create a frame with scrollbar for documentation
        doc_container = ttk.Frame(self.docs_frame)
        doc_container.pack(fill=tk.BOTH, expand=True)
        
        # Documentation text widget
        self.doc_text = tk.Text(doc_container, wrap=tk.WORD, padx=15, pady=15)
        self.doc_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Scrollbar for documentation
        doc_scrollbar = ttk.Scrollbar(doc_container, orient="vertical", command=self.doc_text.yview)
        doc_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.doc_text.configure(yscrollcommand=doc_scrollbar.set)
        
        # Configure tags for documentation formatting
        self.doc_text.tag_configure("heading1", font=("Arial", 16, "bold"), spacing1=10, spacing3=10)
        self.doc_text.tag_configure("heading2", font=("Arial", 14, "bold"), spacing1=8, spacing3=5)
        self.doc_text.tag_configure("heading3", font=("Arial", 12, "bold"), spacing1=5, spacing3=3)
        self.doc_text.tag_configure("code", font=("Courier", 10), background="#f0f0f0", spacing1=5, spacing3=5)
        self.doc_text.tag_configure("formula", font=("Courier", 10, "bold"), background="#e6f2ff", spacing1=3, spacing3=3)
        self.doc_text.tag_configure("note", font=("Arial", 10, "italic"), foreground="#555555")
        self.doc_text.tag_configure("warning", font=("Arial", 10), foreground="#cc0000")
        self.doc_text.tag_configure("normal", spacing1=2, spacing3=2)
        
        # Add the documentation content
        self.populate_documentation()
    
    def populate_documentation(self):
        """Add all documentation content to the documentation tab"""
        # Main title
        self.doc_text.insert(tk.END, "Throne & Liberty Healer Calculator Documentation\n", "heading1")
        
        # About section
        self.doc_text.insert(tk.END, "About This Tool\n", "heading2")
        self.doc_text.insert(tk.END, """This calculator helps healers in Throne & Liberty optimize their stats by comparing different stat distributions and visualizing diminishing returns. The tool uses Monte Carlo simulation to account for critical hits and heavy attack chances.\n\n""", "normal")
        
        # Base Healing Calculation
        self.doc_text.insert(tk.END, "Base Healing Calculations\n", "heading2")
        self.doc_text.insert(tk.END, """The calculator uses the Swift Healing skill at level 15 as the baseline, which:\n""", "normal")
        self.doc_text.insert(tk.END, """• "Restores an ally's Health equal to 610% of Base Damage + 232 damage"\n\n""", "formula")
        
        # Core Formulas
        self.doc_text.insert(tk.END, "Core Formulas\n", "heading3")
        
        self.doc_text.insert(tk.END, "Skill Damage Calculation:\n", "normal")
        self.doc_text.insert(tk.END, """Min Skill Damage = (Base Min Damage × 6.1) + 232
Max Skill Damage = (Base Max Damage × 6.1) + 232\n\n""", "code")
        
        self.doc_text.insert(tk.END, "Healing Output:\n", "normal")
        self.doc_text.insert(tk.END, """Min Heal = Min Skill Damage × (1 + Effective SDB) × (1 + Skill Heal%)
Max Heal = Max Skill Damage × (1 + Effective SDB) × (1 + Skill Heal%)\n\n""", "code")
        
        # MaxRoll Curves
        self.doc_text.insert(tk.END, "Stat Effectiveness (MaxRoll Curves)\n", "heading3")
        self.doc_text.insert(tk.END, """T&L uses diminishing returns curves for stats. The calculator uses the following MaxRoll formulas:\n\n""", "normal")
        
        self.doc_text.insert(tk.END, "Skill Damage Boost (SDB):\n", "normal")
        self.doc_text.insert(tk.END, """Effective SDB = SDB / (SDB + 3000)\n""", "formula")
        self.doc_text.insert(tk.END, """• Soft cap at 1500 (33.3% effectiveness)
• Hard cap at 3000 (50% effectiveness)\n\n""", "normal")
        
        self.doc_text.insert(tk.END, "Critical Hit Chance:\n", "normal")
        self.doc_text.insert(tk.END, """Effective Crit% = Crit / (Crit + 6000)\n""", "formula")
        self.doc_text.insert(tk.END, """• Soft cap at 3000 (33.3% effectiveness) 
• Hard cap at 6000 (50% effectiveness)\n\n""", "normal")
        
        self.doc_text.insert(tk.END, "Heavy Attack Chance (HAC):\n", "normal")
        self.doc_text.insert(tk.END, """Effective HAC% = HAC / (HAC + 1000)\n""", "formula")
        self.doc_text.insert(tk.END, """• Soft cap at 500 (33.3% effectiveness)
• Hard cap at 1000 (50% effectiveness)\n\n""", "normal")
        
        # Simulation Explanation
        self.doc_text.insert(tk.END, "Understanding Simulation Results\n", "heading2")
        self.doc_text.insert(tk.END, """The calculator runs Monte Carlo simulations to account for randomness in healing:
• Base healing is randomized between min and max values
• Critical hits guarantee maximum healing value
• Heavy attacks double healing output
• Both can occur simultaneously for maximum effect\n\n""", "normal")
        
        # Usage Guide
        self.doc_text.insert(tk.END, "How to Use the Calculator\n", "heading2")
        self.doc_text.insert(tk.END, """1. Enter your base character stats
2. Configure runes you want to compare
3. Adjust the number of simulation trials (more trials = more accurate results but slower performance)
4. Click "Calculate" to run the simulation
5. Review ranked results and examine effectiveness curves\n\n""", "normal")
        
        # Graph Interpretation
        self.doc_text.insert(tk.END, "Interpreting Stat Curves\n", "heading2")
        self.doc_text.insert(tk.END, """The graph tabs show:
• Top Graph: Average healing output as stat value increases
• Bottom Graph: Effective percentage of the stat based on MaxRoll formula
• Vertical Lines: Your current value (red) and soft cap (orange)

The curves help visualize diminishing returns, showing where additional stat points give less benefit.\n\n""", "normal")
        
        # Advanced Settings
        self.doc_text.insert(tk.END, "Advanced Settings\n", "heading2")
        self.doc_text.insert(tk.END, """Use the simulation controls to balance accuracy vs. performance:
• Default: 10,000 trials (good balance)
• Minimum: 1,000 trials (faster but less accurate)
• Maximum: 100,000 trials (very accurate but may slow down older computers)\n\n""", "normal")
        
        self.doc_text.insert(tk.END, """Warning: Setting trials above 100,000 may cause significant performance issues on some systems.\n""", "warning")
        
        # Make the text read-only
        self.doc_text.configure(state="disabled")
    
    def calculate_comparison(self):
        try:
            # Get trials count
            trials = int(self.custom_trials_var.get())
            
            # Get base stats
            base_min_damage = float(self.base_min_damage_var.get())
            base_max_damage = float(self.base_max_damage_var.get())
            skill_heal = float(self.skill_heal_var.get()) / 100  # Convert to decimal
            sdb = float(self.sdb_var.get())
            hac = float(self.hac_var.get())
            crit = float(self.crit_var.get())
            
            # Warn if trials are very high
            if trials > 100000:
                result = messagebox.askyesno(
                    "Performance Warning", 
                    f"You are about to run {trials:,} trials, which may cause slowdowns. Continue anyway?"
                )
                if not result:
                    return
            
            # Calculate base case
            base_result = calculate_heal(base_min_damage, base_max_damage, skill_heal, sdb, hac, crit, trials)
            
            results = {"Base Stats": base_result}
            
            # Calculate results for each enabled rune
            for i in range(4):
                if self.rune_enabled_vars[i].get():
                    rune_type = self.rune_type_vars[i].get()
                    if not rune_type:
                        continue
                        
                    rune_value_str = self.rune_value_vars[i].get()
                    if not rune_value_str:
                        continue
                        
                    rune_value = float(rune_value_str)
                    rune_name = self.rune_names[i].get() or f"Rune {i+1}"
                    
                    # Apply rune effect
                    new_sdb = sdb
                    new_hac = hac
                    new_crit = crit
                    new_skill_heal = skill_heal
                    
                    if rune_type == "Skill Damage Boost":
                        new_sdb += rune_value
                    elif rune_type == "Heavy Attack Chance":
                        new_hac += rune_value
                    elif rune_type == "Crit Chance":
                        new_crit += rune_value
                    elif rune_type == "Skill Heal":
                        new_skill_heal += rune_value / 100  # Convert to decimal
                    
                    # Calculate with rune
                    rune_result = calculate_heal(base_min_damage, base_max_damage, new_skill_heal, new_sdb, new_hac, new_crit, trials)
                    results[rune_name] = rune_result
            
            # Display results
            self.display_results(results)
            
            # Analyze stat effectiveness curves
            self.analyze_and_display_stat_curves(base_min_damage, base_max_damage, skill_heal, sdb, hac, crit)
            
        except ValueError as e:
            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(tk.END, f"Error: {str(e)}\nPlease enter valid numbers for all fields.")
    
    def display_results(self, results):
        # Sort results by average heal (descending)
        sorted_results = sorted(results.items(), key=lambda x: x[1]['avg_heal'], reverse=True)
        
        # Clear previous results
        self.results_text.delete(1.0, tk.END)
        
        # Add header explaining how to read results
        self.results_text.insert(tk.END, "RESULTS RANKED BY EFFECTIVENESS\n", "Header.TLabel")
        self.results_text.insert(tk.END, "Check stat curves in tabs to see diminishing returns\n\n")
        
        # Add results for each build
        rank = 1
        for build_name, data in sorted_results:
            percent_increase = ""
            if build_name != "Base Stats":
                base_heal = results["Base Stats"]["avg_heal"]
                increase = ((data['avg_heal'] - base_heal) / base_heal) * 100
                percent_increase = f" (+{increase:.2f}%)"
            
            self.results_text.insert(tk.END, f"#{rank}: {build_name}{percent_increase}\n", "Result.TLabel")
            self.results_text.insert(tk.END, f"  Average Heal: {data['avg_heal']:.2f}\n")
            self.results_text.insert(tk.END, f"  Min/Max: {data['min_heal']:.0f} - {data['max_heal']:.0f}\n")
            self.results_text.insert(tk.END, f"  Effective Stats:\n")
            self.results_text.insert(tk.END, f"    SDB: {data['sdb']:.0f} → {data['sdb_maxroll']*100:.2f}%\n")
            self.results_text.insert(tk.END, f"    Crit: {data['crit']:.0f} → {data['crit_maxroll']*100:.2f}%\n")
            self.results_text.insert(tk.END, f"    HAC: {data['hac']:.0f} → {data['hac_maxroll']*100:.2f}%\n")
            self.results_text.insert(tk.END, f"  Proc Chances:\n")
            self.results_text.insert(tk.END, f"    Crit: {data['crit_percentage']:.2f}%\n")
            self.results_text.insert(tk.END, f"    HAC: {data['hac_percentage']:.2f}%\n")
            self.results_text.insert(tk.END, f"    Crit+HAC: {data['crit_hac_percentage']:.2f}%\n\n")
            rank += 1
    
    def analyze_and_display_stat_curves(self, base_min_damage, base_max_damage, skill_heal, sdb, hac, crit):
        # Analyze each stat's effectiveness
        sdb_analysis = analyze_stat_effectiveness(base_min_damage, base_max_damage, skill_heal, sdb, hac, crit, "sdb")
        hac_analysis = analyze_stat_effectiveness(base_min_damage, base_max_damage, skill_heal, sdb, hac, crit, "hac")
        crit_analysis = analyze_stat_effectiveness(base_min_damage, base_max_damage, skill_heal, sdb, hac, crit, "crit")
        
        # Plot SDB curve
        self.plot_stat_curve(
            self.sdb_figure, 
            self.sdb_canvas,
            sdb_analysis, 
            "Skill Damage Boost", 
            "sdb", 
            sdb, 
            3000
        )
        
        # Plot HAC curve
        self.plot_stat_curve(
            self.hac_figure, 
            self.hac_canvas,
            hac_analysis, 
            "Heavy Attack Chance", 
            "hac", 
            hac, 
            1000
        )
        
        # Plot Crit curve
        self.plot_stat_curve(
            self.crit_figure, 
            self.crit_canvas,
            crit_analysis, 
            "Critical Hit Chance", 
            "crit", 
            crit, 
            6000
        )
    
    def plot_stat_curve(self, figure, canvas, analysis_data, stat_name, stat_key, current_value, cap_value):
        # Clear the figure
        figure.clear()
        
        # Create subplot grid
        gs = figure.add_gridspec(2, 1, height_ratios=[2, 1])
        
        # Extract data for plotting
        stat_values = [item["value"] for item in analysis_data]
        heal_values = [item["avg_heal"] for item in analysis_data]
        effective_values = [item[f"{stat_key}_maxroll"] * 100 for item in analysis_data]
        
        # Calculate marginal effectiveness
        marginal_effectiveness = []
        for i in range(1, len(heal_values)):
            delta_stat = stat_values[i] - stat_values[i-1]
            delta_heal = heal_values[i] - heal_values[i-1]
            if delta_stat > 0:
                effectiveness = delta_heal / delta_stat
                marginal_effectiveness.append(effectiveness)
            else:
                marginal_effectiveness.append(0)
        # Add a placeholder for the first point
        marginal_effectiveness = [marginal_effectiveness[0]] + marginal_effectiveness
        
        # Plot the heal curve
        ax1 = figure.add_subplot(gs[0])
        line1, = ax1.plot(stat_values, heal_values, 'b-', label='Avg Heal')
        ax1.set_ylabel('Average Heal', color='b')
        ax1.tick_params(axis='y', labelcolor='b')
        ax1.set_title(f'{stat_name} Effectiveness Curve')
        ax1.grid(True, alpha=0.3)
        
        # Add vertical line for current value
        ax1.axvline(x=current_value, color='r', linestyle='--', alpha=0.7, 
                   label=f'Current ({current_value:.0f})')
        
        # Add soft cap indicator
        ax1.axvline(x=cap_value/2, color='orange', linestyle=':', alpha=0.7,
                   label=f'Soft Cap ({cap_value/2:.0f})')
                   
        # Add text labels - moved to avoid overlap
        current_y = np.interp(current_value, stat_values, heal_values)
        ax1.annotate('', xy=(current_value, current_y), xytext=(20, -30),
             textcoords="offset points",
             arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=.2"))

        
        # Plot the maxroll/effectiveness curve
        ax2 = figure.add_subplot(gs[1])
        ax2.plot(stat_values, effective_values, 'g-', label='Stat %')
        ax2.set_ylabel('Effective %', color='g')
        ax2.set_xlabel(f'{stat_name} Value')
        ax2.tick_params(axis='y', labelcolor='g')
        ax2.set_ylim(0, 100)
        ax2.grid(True, alpha=0.3)
        
        # Add text showing current effectiveness - moved to avoid overlap
        current_effect = np.interp(current_value, stat_values, effective_values)
        ax2.annotate(f'{current_effect:.1f}%',
                    xy=(current_value, current_effect),
                    xytext=(15, 10),  # Adjusted position
                    textcoords="offset points",
                    arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=.2"))
                    
        # Add vertical lines to the second plot too
        ax2.axvline(x=current_value, color='r', linestyle='--', alpha=0.7)
        ax2.axvline(x=cap_value/2, color='orange', linestyle=':', alpha=0.7)
        
        ax1.legend(loc='upper left', bbox_to_anchor=(1, 1))

        # Add key stats to the plot - moved to better position
        textstr = f'''
Current {stat_name}: {current_value:.0f}
Effective %: {current_effect:.1f}%
Avg Heal: {current_y:.0f}
Soft Cap: {cap_value/2:.0f}
Hard Cap: {cap_value:.0f}
'''     
        # Stats Box
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        ax1.text(1.02, -0.3, textstr, transform=ax1.transAxes, fontsize=8,
        verticalalignment='top', horizontalalignment='left', bbox=props)


        
        figure.tight_layout()
        canvas.draw()

if __name__ == "__main__":
    root = tk.Tk()
    app = HealCalcApp(root)
    root.mainloop()
import json
import os
import threading
import time
import customtkinter as ctk
from tkinter import filedialog
from google import genai
from google.genai import types
from pydantic import BaseModel, Field

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

c_bg = "#080710"
c_panel = "#110E1F"
c_elem = "#1A152E"
c_cyan = "#00F0FF"
c_cyan_h = "#00ADB5"
c_pink = "#FF007F"
c_txt = "#00FFC6"

db = {
    "Porsche": {
        "911 GT2 RS": 3241,
        "911 GT3 RS": 3268,
        "911 Carrera S": 3298,
        "718 Cayman GT4": 3000,
        "918 Spyder": 3612,
        "911 GT1 Strassenversion": 2535
    },
    "Ferrari": {
        "F8 Tributo": 3163,
        "488 Pista": 2822,
        "LaFerrari": 3492,
        "SF90 Stradale": 3461,
        "F40": 2755,
        "812 Superfast": 3593,
        "Enzo Ferrari": 3262
    },
    "Lamborghini": {
        "Huracán Performante": 3047,
        "Aventador SVJ": 3364,
        "Gallardo Superleggera": 2932,
        "Sian FKP 37": 3595,
        "Countach": 3280
    },
    "Nissan": {
        "GT-R NISMO (R35)": 3865,
        "Skyline GT-R (R34)": 3439,
        "Silvia S15": 2733,
        "370Z NISMO": 3437,
        "Fairlady Z (Z33)": 3247
    },
    "BMW": {
        "M3 Competition": 3840,
        "M4 GTS": 3329,
        "M2 CS": 3532,
        "M5 CS": 4110,
        "M1 Procar": 2866,
        "Z4 M Coupe": 3230
    },
    "Toyota": {
        "GR Supra": 3400,
        "Supra RZ (A80)": 3450,
        "GR Yaris": 2822,
        "AE86 Trueno": 2200,
        "2000GT": 2425
    },
    "Chevrolet": {
        "Corvette Z06 (C8)": 3434,
        "Corvette ZR1 (C7)": 3560,
        "Camaro ZL1 1LE": 3883,
        "Chevelle SS": 3450
    },
    "Ford": {
        "Mustang Shelby GT500": 4225,
        "Ford GT": 3354,
        "Mustang Mach 1": 3788,
        "Escort RS Cosworth": 2778,
        "Focus RS": 3459
    },
    "McLaren": {
        "720S Coupe": 3128,
        "765LT": 2954,
        "Senna": 2641,
        "P1": 3075,
        "600LT Spider": 2981,
        "F1 GT": 2667
    },
    "Audi": {
        "R8 V10 Performance": 3593,
        "RS6 Avant": 4965,
        "RS4 Avant": 3990,
        "Sport Quattro": 2866,
        "TT RS": 3593
    },
    "Mercedes-AMG": {
        "AMG GT Black Series": 3616,
        "AMG One": 3737,
        "C63 S Coupe": 3825,
        "E63 S": 4555,
        "CLK GTR": 3175
    },
    "Honda": {
        "Civic Type R (FK8)": 3117,
        "NSX Type R": 2711,
        "S2000 CR": 2810,
        "Civic CRX Si": 2138
    },
    "Subaru": {
        "WRX STI S209": 3686,
        "Impreza 22B STi": 2800,
        "BRZ": 2815
    },
    "Other / Custom": {
        "Type custom car model below...": ""
    }
}

hw_list = [
    "Controller / Gamepad (Xbox / PlayStation)",
    "Fanatec GT DD Pro / CSL DD / DD1 / DD2",
    "Moza Racing (R3 / R5 / R9 / R12 / R16 / R21)",
    "Simucube 2 (Sport / Pro / Ultimate)",
    "Thrustmaster T300RS / TX / T-GT II / TS-XW",
    "Thrustmaster T248 / T150 / TMX",
    "Thrustmaster T-818 Direct Drive",
    "Logitech G PRO Direct Drive",
    "Logitech G29 / G920 / G923",
    "Asetek SimSports (La Prima / Forte / Invicta)",
    "Cammus (C5 / C12)",
    "Custom / Other Wheel Base"
]

pi_list = ["S1", "A", "S2", "X", "B", "C", "D"]

class P1(BaseModel):
    front: float = Field(description="Front value")
    rear: float = Field(description="Rear value")

class P2(BaseModel):
    front: str = Field(description="Front setting or angle")
    rear: str = Field(description="Rear setting or angle")

class MAlign(BaseModel):
    camber: P2
    toe: P2
    caster: str

class MDiff(BaseModel):
    acceleration: P2
    deceleration: P2

class MBrake(BaseModel):
    balance_bias: str
    pressure: str

class MConfig(BaseModel):
    car_name: str
    build_type: str
    tire_pressure_psi: P1
    final_drive_ratio: float
    alignment: MAlign
    anti_roll_bars: P1
    springs: P1
    damping_rebound: P1
    damping_bump: P1
    aero_downforce: P2
    brakes: MBrake
    differential: MDiff
    sim_wheel_telemetry_notes: str = Field(description="Notes")

def build_sheet(d):
    out = []
    out.append("────────────────────────────────────────────────────────────")
    out.append("              VEX TUNER // FORZA EDITION")
    out.append("────────────────────────────────────────────────────────────")
    out.append(f" VEHICLE : {d.get('car_name', 'N/A').upper()}")
    out.append(f" PROFILE : {d.get('build_type', 'N/A').upper()}")
    out.append("────────────────────────────────────────────────────────────")
    out.append("")

    tp = d.get("tire_pressure_psi", {})
    out.append("01. TIRES & GEARING")
    out.append("    ────────────────────────────────────────────────────")
    out.append(f"    • Front Tire Pressure : {tp.get('front', '-')} PSI")
    out.append(f"    • Rear Tire Pressure  : {tp.get('rear', '-')} PSI")
    out.append(f"    • Final Drive Ratio   : {d.get('final_drive_ratio', '-')}")
    out.append("")

    al = d.get("alignment", {})
    cb = al.get("camber", {})
    to = al.get("toe", {})
    out.append("02. ALIGNMENT")
    out.append("    ────────────────────────────────────────────────────")
    out.append(f"    • Camber (F / R)      : {cb.get('front', '-')}  /  {cb.get('rear', '-')}")
    out.append(f"    • Toe (F / R)         : {to.get('front', '-')}  /  {to.get('rear', '-')}")
    out.append(f"    • Caster              : {al.get('caster', '-')}")
    out.append("")

    ar = d.get("anti_roll_bars", {})
    sp = d.get("springs", {})
    rb = d.get("damping_rebound", {})
    bm = d.get("damping_bump", {})
    out.append("03. CHASSIS & SUSPENSION")
    out.append("    ────────────────────────────────────────────────────")
    out.append(f"    • Anti-Roll Bars (F/R): {ar.get('front', '-')}  /  {ar.get('rear', '-')}")
    out.append(f"    • Spring Rates (F/R)  : {sp.get('front', '-')} lb/in  /  {sp.get('rear', '-')} lb/in")
    out.append(f"    • Rebound Damping     : {rb.get('front', '-')}  /  {rb.get('rear', '-')}")
    out.append(f"    • Bump Damping        : {bm.get('front', '-')}  /  {bm.get('rear', '-')}")
    out.append("")

    ae = d.get("aero_downforce", {})
    br = d.get("brakes", {})
    out.append("04. AERO & BRAKES")
    out.append("    ────────────────────────────────────────────────────")
    out.append(f"    • Downforce (F / R)   : {ae.get('front', '-')}  /  {ae.get('rear', '-')}")
    out.append(f"    • Brake Balance Bias  : {br.get('balance_bias', '-')}")
    out.append(f"    • Brake Pressure      : {br.get('pressure', '-')}")
    out.append("")

    df = d.get("differential", {})
    ac = df.get("acceleration", {})
    dc = df.get("deceleration", {})
    out.append("05. DIFFERENTIAL SETTINGS")
    out.append("    ────────────────────────────────────────────────────")
    out.append(f"    • Acceleration (F/R)  : {ac.get('front', '-')}  /  {ac.get('rear', '-')}")
    out.append(f"    • Deceleration (F/R)  : {dc.get('front', '-')}  /  {dc.get('rear', '-')}")
    out.append("")

    nt = d.get("sim_wheel_telemetry_notes", "")
    out.append("06. CONTROLLER / WHEEL SETUP NOTES")
    out.append("    ────────────────────────────────────────────────────")
    
    words = nt.split()
    curr = "    "
    for w in words:
        if len(curr) + len(w) + 1 > 58:
            out.append(curr)
            curr = "    " + w
        else:
            curr += (" " if curr != "    " else "") + w
    if curr.strip():
        out.append(curr)

    out.append("")
    out.append("────────────────────────────────────────────────────────────")
    return "\n".join(out)

class AppMain(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("VEX TUNER - FORZA EDITION")
        self.geometry("960x990")
        self.configure(fg_color=c_bg)
        self.current_data = None  
        self.busy = False

        try:
            import ctypes
            self.update()
            dw = 20
            set_attr = ctypes.windll.dwmapi.DwmSetWindowAttribute
            get_p = ctypes.windll.user32.GetParent
            hwnd = get_p(self.winfo_id())
            set_attr(hwnd, dw, ctypes.byref(ctypes.c_int(1)), 4)
        except Exception:
            pass

        self.f_left = ctk.CTkFrame(self, width=365, fg_color=c_panel, border_color=c_cyan, border_width=2, corner_radius=8)
        self.f_left.pack(side="left", fill="y", padx=15, pady=15)

        ctk.CTkLabel(self.f_left, text="VEX TUNER", font=("Consolas", 22, "bold"), text_color=c_cyan).pack(pady=(12, 2))
        ctk.CTkLabel(self.f_left, text="[ CONTROLLER & WHEEL TUNING ENGINE ]", font=("Consolas", 10, "bold"), text_color=c_pink).pack(pady=(0, 10))

        ctk.CTkLabel(self.f_left, text="License Key:", font=("Consolas", 11), text_color="#E0E0E0").pack(anchor="w", padx=12)
        self.e_key = ctk.CTkEntry(self.f_left, show="*", placeholder_text="Enter license credentials", border_color="#2D254A", border_width=2, fg_color=c_elem, corner_radius=6)
        self.e_key.pack(fill="x", padx=12, pady=(0, 6))

        ctk.CTkLabel(self.f_left, text="Select Car Brand:", font=("Consolas", 11), text_color="#E0E0E0").pack(anchor="w", padx=12)
        self.cb_brand = ctk.CTkComboBox(self.f_left, values=list(db.keys()), command=self.ch_brand, border_color="#2D254A", button_color=c_cyan, button_hover_color=c_cyan_h, fg_color=c_elem, corner_radius=6)
        self.cb_brand.pack(fill="x", padx=12, pady=(0, 6))

        ctk.CTkLabel(self.f_left, text="Select Model or Type Custom:", font=("Consolas", 11), text_color="#E0E0E0").pack(anchor="w", padx=12)
        self.cb_model = ctk.CTkComboBox(self.f_left, values=list(db["Porsche"].keys()), command=self.ch_model, border_color="#2D254A", button_color=c_cyan, button_hover_color=c_cyan_h, fg_color=c_elem, corner_radius=6)
        self.cb_model.pack(fill="x", padx=12, pady=(0, 6))

        ctk.CTkLabel(self.f_left, text="Car Weight (lbs - optional):", font=("Consolas", 11), text_color="#E0E0E0").pack(anchor="w", padx=12)
        self.e_weight = ctk.CTkEntry(self.f_left, placeholder_text="e.g. 3200 (or leave blank)", border_color="#2D254A", border_width=2, fg_color=c_elem, corner_radius=6)
        self.e_weight.pack(fill="x", padx=12, pady=(0, 6))
        self.e_weight.insert(0, str(db["Porsche"]["911 GT2 RS"]))

        ctk.CTkLabel(self.f_left, text="PI Class Target:", font=("Consolas", 11), text_color="#E0E0E0").pack(anchor="w", padx=12)
        self.om_pi = ctk.CTkOptionMenu(self.f_left, values=pi_list, fg_color=c_elem, button_color=c_cyan, button_hover_color=c_cyan_h, text_color="#FFFFFF", font=("Consolas", 11, "bold"), corner_radius=6)
        self.om_pi.pack(fill="x", padx=12, pady=(0, 6))

        ctk.CTkLabel(self.f_left, text="Drivetrain:", font=("Consolas", 11), text_color="#E0E0E0").pack(anchor="w", padx=12)
        self.om_drive = ctk.CTkOptionMenu(self.f_left, values=["AWD", "RWD", "FWD"], fg_color=c_elem, button_color=c_cyan, button_hover_color=c_cyan_h, text_color="#FFFFFF", font=("Consolas", 12, "bold"), corner_radius=6)
        self.om_drive.pack(fill="x", padx=12, pady=(0, 6))

        ctk.CTkLabel(self.f_left, text="Controller / Wheel Hardware:", font=("Consolas", 11), text_color="#E0E0E0").pack(anchor="w", padx=12)
        self.om_hw = ctk.CTkOptionMenu(self.f_left, values=hw_list, fg_color=c_elem, button_color=c_cyan, button_hover_color=c_cyan_h, text_color="#FFFFFF", font=("Consolas", 11, "bold"), corner_radius=6)
        self.om_hw.pack(fill="x", padx=12, pady=(0, 6))

        ctk.CTkLabel(self.f_left, text="Handling Profile:", font=("Consolas", 11), text_color="#E0E0E0").pack(anchor="w", padx=12)
        self.om_style = ctk.CTkOptionMenu(self.f_left, values=["Sim Racing / Real Physics", "Road Race", "Drift", "Rally / Offroad", "Drag"], fg_color=c_elem, button_color=c_cyan, button_hover_color=c_cyan_h, text_color="#FFFFFF", font=("Consolas", 12, "bold"), corner_radius=6)
        self.om_style.pack(fill="x", padx=12, pady=(0, 6))

        ctk.CTkLabel(self.f_left, text="Custom Instructions / Prompt:", font=("Consolas", 11), text_color="#E0E0E0").pack(anchor="w", padx=12)
        self.tb_custom = ctk.CTkTextbox(self.f_left, height=35, border_color="#2D254A", border_width=2, fg_color=c_elem, text_color="#FFFFFF", font=("Consolas", 11), corner_radius=6)
        self.tb_custom.pack(fill="x", padx=12, pady=(0, 6))

        self.btn_gen = ctk.CTkButton(self.f_left, text="BUILD TUNE", font=("Consolas", 13, "bold"), fg_color=c_pink, hover_color="#C70063", text_color="#FFFFFF", height=36, corner_radius=8, border_width=1, border_color="#FF529B", command=lambda: self.run_task(False))
        self.btn_gen.pack(fill="x", padx=12, pady=4)

        self.lbl_status = ctk.CTkLabel(self.f_left, text="SYSTEM READY", font=("Consolas", 10), text_color="gray")
        self.lbl_status.pack(pady=2)

        self.f_right = ctk.CTkFrame(self, fg_color=c_panel, border_color=c_cyan, border_width=2, corner_radius=8)
        self.f_right.pack(side="right", fill="both", expand=True, padx=(0, 15), pady=15)

        f_hdr = ctk.CTkFrame(self.f_right, fg_color="transparent")
        f_hdr.pack(fill="x", padx=12, pady=(10, 2))

        ctk.CTkLabel(f_hdr, text="TUNE SHEET", font=("Consolas", 16, "bold"), text_color=c_cyan).pack(side="left")

        self.btn_open = ctk.CTkButton(f_hdr, text="OPEN TUNE", font=("Consolas", 10, "bold"), fg_color=c_elem, hover_color="#2D254A", text_color=c_cyan, width=90, height=28, corner_radius=6, border_width=1, border_color=c_cyan, command=self.load_file)
        self.btn_open.pack(side="right", padx=(6, 0))

        self.btn_save = ctk.CTkButton(f_hdr, text="SAVE TUNE", font=("Consolas", 10, "bold"), fg_color=c_elem, hover_color="#2D254A", text_color=c_txt, width=90, height=28, corner_radius=6, border_width=1, border_color=c_txt, command=self.save_file)
        self.btn_save.pack(side="right")

        self.tb_out = ctk.CTkTextbox(self.f_right, font=("Consolas", 11), text_color=c_txt, fg_color="#06050A", border_color="#2D254A", border_width=2, corner_radius=6, state="disabled")
        self.tb_out.pack(fill="both", expand=True, padx=12, pady=(6, 8))

        ctk.CTkLabel(self.f_right, text="ADJUST SETUP & FIX HANDLING PROBLEMS", font=("Consolas", 11, "bold"), text_color=c_pink).pack(anchor="w", padx=12, pady=(2, 2))

        self.tb_adj = ctk.CTkTextbox(self.f_right, height=35, border_color="#2D254A", border_width=2, fg_color=c_elem, text_color="#FFFFFF", font=("Consolas", 11), corner_radius=6)
        self.tb_adj.pack(fill="x", padx=12, pady=(0, 6))

        self.btn_adj = ctk.CTkButton(self.f_right, text="ADJUST TUNE", font=("Consolas", 12, "bold"), fg_color=c_cyan, hover_color=c_cyan_h, text_color="#080710", height=34, corner_radius=6, border_width=1, border_color="#73F7FF", command=lambda: self.run_task(True))
        self.btn_adj.pack(fill="x", padx=12, pady=(0, 10))

    def ch_brand(self, val):
        m_dict = db.get(val, {"Type custom model...": ""})
        m_names = list(m_dict.keys())
        self.cb_model.configure(values=m_names)
        self.cb_model.set(m_names[0])
        self.ch_model(m_names[0])

    def ch_model(self, val):
        b_val = self.cb_brand.get()
        m_dict = db.get(b_val, {})
        wt = m_dict.get(val, "")
        self.e_weight.delete(0, "end")
        if wt != "":
            self.e_weight.insert(0, str(wt))

    def write_out(self, txt):
        self.tb_out.configure(state="normal")
        self.tb_out.delete("1.0", "end")
        self.tb_out.insert("1.0", txt)
        self.tb_out.configure(state="disabled")

    def save_file(self):
        if not self.current_data:
            self.lbl_status.configure(text="ERROR: NO ACTIVE TUNE TO SAVE", text_color="#FF007F")
            return
        path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON Tune Files", "*.json"), ("All Files", "*.*")], title="Save Forza Tune")
        if path:
            try:
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(self.current_data, f, indent=4)
                self.lbl_status.configure(text="TUNE SAVED SUCCESSFULLY", text_color="#00FFC6")
            except Exception as e:
                self.lbl_status.configure(text=f"ERROR SAVING FILE: {str(e)}", text_color="#FF007F")

    def load_file(self):
        path = filedialog.askopenfilename(filetypes=[("JSON Tune Files", "*.json"), ("All Files", "*.*")], title="Open Forza Tune")
        if path:
            try:
                with open(path, "r", encoding="utf-8") as f:
                    d = json.load(f)
                if isinstance(d, dict) and "car_name" in d:
                    self.current_data = d
                    self.write_out(build_sheet(d))
                    self.lbl_status.configure(text="TUNE LOADED & READY FOR ADJUSTMENTS", text_color="#00FFC6")
                else:
                    self.lbl_status.configure(text="ERROR: INVALID TUNE FILE FORMAT", text_color="#FF007F")
            except Exception as e:
                self.lbl_status.configure(text=f"ERROR OPENING FILE: {str(e)}", text_color="#FF007F")

    def anim_load(self, msg):
        blocks = ["[>                 ]", "[==                ]", "[===               ]",
                  "[====              ]", "[=====             ]", "[======            ]",
                  "[=======           ]", "[========          ]", "[=========         ]",
                  "[==========        ]", "[===========       ]", "[============      ]",
                  "[=============     ]", "[==============    ]", "[===============   ]",
                  "[================  ]", "[================= ]", "[==================]"]
        idx = 0
        while self.busy:
            t = f"\n\n\n\n    {msg.upper()}\n    {blocks[idx]}\n    [ SECURING TELEMETRY, WEIGHT SPECS & CHASSIS DYNAMICS ]"
            self.after(0, self.write_out, t)
            idx = (idx + 1) % len(blocks)
            time.sleep(0.08)

    def run_task(self, adj=False):
        key = self.e_key.get().strip() or os.environ.get("GEMINI_API_KEY", "")
        if not key:
            self.lbl_status.configure(text="ERROR: PLEASE ENTER YOUR LICENSE KEY ABOVE", text_color="#FF007F")
            return
        if adj and not self.current_data:
            self.lbl_status.configure(text="ERROR: GENERATE OR OPEN A TUNE FIRST BEFORE ADJUSTING", text_color="#FF007F")
            return

        self.btn_gen.configure(state="disabled")
        self.btn_adj.configure(state="disabled")
        self.btn_save.configure(state="disabled")
        self.btn_open.configure(state="disabled")
        self.busy = True

        if adj:
            self.lbl_status.configure(text="RECALCULATING & ADJUSTING TUNE...", text_color="#00F0FF")
            threading.Thread(target=self.anim_load, args=("RE-CALIBRATING SETUP...",), daemon=True).start()
        else:
            self.lbl_status.configure(text="GENERATING FORZA TUNE SHEET...", text_color="#00F0FF")
            threading.Thread(target=self.anim_load, args=("COMPUTING WEIGHT & PHYSICS MATRIX...",), daemon=True).start()

        threading.Thread(target=self.exec_backend, args=(key, adj), daemon=True).start()

    def exec_backend(self, key, adj=False):
        try:
            cl = genai.Client(api_key=key)
            c_name = f"{self.cb_brand.get()} {self.cb_model.get()}".strip()
            dev = self.om_hw.get()
            wt_raw = self.e_weight.get().strip()
            wt_spec = f"Specified Weight: {wt_raw} lbs" if wt_raw else "No weight specified (auto-estimate standard curb weight)"

            if adj:
                fb = self.tb_adj.get("1.0", "end-1c").strip()
                pld = f"""
                You are adjusting an existing vehicle simulation tuning configuration to resolve specific handling dynamics.
                Previous Configuration Data (JSON):
                {json.dumps(self.current_data)}

                Vehicle Weight / Mass Spec: {wt_spec}
                User Adjustments / Requested Fixes: "{fb}"
                Hardware/Device Profile: {dev}

                Instructions:
                Recalculate and modify parameters to address the reported feedback while maintaining proper vehicle weight transfer and balance physics.
                """
            else:
                cust = self.tb_custom.get("1.0", "end-1c").strip()
                pld = f"""
                You are an advanced mathematical vehicle dynamics simulator and motorsport configuration engineer.
                Generate a precision setup calculation tailored for the specified hardware and platform specs:
                - Vehicle: {c_name}
                - Vehicle Weight Spec: {wt_spec}
                - Target Performance Class: {self.om_pi.get()}
                - Drivetrain Layout: {self.om_drive.get()}
                - Control Input Device / Hardware: {dev}
                - Target Handling Style: {self.om_style.get()}

                Calculation Rules:
                1. VEHICLE MASS & DYNAMICS: Factor in weight, balance, and weight transfer.
                2. HARDWARE OPTIMIZATION: Tailor feedback and response curves for {dev}.
                3. Additional Parameters: {cust}
                """

            models = ['gemini-3.5-flash', 'gemini-2.5-flash', 'gemini-2.0-flash']
            res = None
            err_last = None

            for m in models:
                try:
                    res = cl.models.generate_content(
                        model=m,
                        contents=pld,
                        config=types.GenerateContentConfig(
                            response_mime_type="application/json",
                            response_schema=MConfig,
                            temperature=0.2,
                        ),
                    )
                    if res and res.text:
                        break
                except Exception as ex:
                    err_last = ex
                    continue

            self.busy = False
            time.sleep(0.1)

            if res and res.text:
                j_res = json.loads(res.text)
                self.current_data = j_res
                sheet = build_sheet(j_res)
                self.after(0, self.finish_task, sheet, False)
            else:
                raise err_last or Exception("Failed to receive a valid response from the backend service.")

        except Exception as e:
            self.busy = False
            e_msg = str(e)
            if "INVALID_ARGUMENT" in e_msg or "API key" in e_msg:
                friendly = "[AUTHENTICATION ERROR]\n\nPlease check your license key credentials."
            elif "429" in e_msg or "RESOURCE_EXHAUSTED" in e_msg:
                friendly = "[RATE LIMITED]\n\nServer capacity limit reached. Please wait ~30 seconds and try again."
            else:
                friendly = f"Error: {e_msg}"
            self.after(0, self.finish_task, friendly, True)

    def finish_task(self, text, err):
        self.write_out(text)
        self.btn_gen.configure(state="normal")
        self.btn_adj.configure(state="normal")
        self.btn_save.configure(state="normal")
        self.btn_open.configure(state="normal")
        if err:
            self.lbl_status.configure(text="FAILED TO PROCESS CALCULATION", text_color="#FF007F")
        else:
            self.lbl_status.configure(text="TUNE SHEET UPDATED SUCCESSFULLY", text_color="#00FFC6")

if __name__ == "__main__":
    app = AppMain()
    app.mainloop()
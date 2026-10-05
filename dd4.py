"""
DD-DORNIER-CALCULATION  v1.2
Dornier Loom Production Calculator
Run: python DD-DORNIER-CALCULATION.py
Requires: Python 3.8+ (tkinter is standard library)
"""

import tkinter as tk
from tkinter import ttk, messagebox, font as tkfont
import re
from datetime import datetime

# ══════════════════ COLOURS ══════════════════
BG_DARK    = "#0D1B2A"
BG_MID     = "#1B2A3D"
BG_CARD    = "#1E3A5F"
GOLD       = "#FFD700"
CYAN       = "#00E5FF"
GREEN      = "#39FF14"
ORANGE     = "#FF7F00"
PINK       = "#FF6EC7"
WHITE      = "#FFFFFF"
LIGHT      = "#B0C4DE"
ENTRY_BG   = "#0A2540"
ENTRY_FG   = "#00E5FF"
BTN_CALC   = "#FF6B00"
BTN_RESET  = "#CC0055"
BTN_RPT    = "#006400"

# ══════════════════ ENGINE ═══════════════════
def parse_sorts(quality_str):
    m = re.search(r'\b(\d+)\s*[Xx]\s*(\d+)', quality_str)
    return int(m.group(2)) if m else None

def dornier_calc(quality, rpm, loom_diff, ozs, width, sp_val):
    sorts = parse_sorts(quality)
    if sorts is None:
        raise ValueError(
            "Cannot read Sorts from Quality.\n"
            "Format needed:  ... N X M   e.g.  11 X 11"
        )
    hrs100   = 8 * 60 * rpm                          # =8*60*RPM
    sp       = ((sorts * 4) - sp_val) * 10           # sorting pinion
    eff      = ((loom_diff * 1000) / hrs100) * 100   # efficiency %
    gsm      = ozs * 30.51                           # GSM
    gm_m     = (gsm * width) / 39.37                # GM/METER
    meter    = (hrs100 * (eff / 100)) / sp           # production METER
    kg_loom  = meter * (gm_m / 1000)                # KG/LOOM
    ozs_yds  = (ozs / 40) * width                   # OZS/YDS
    return dict(
        SORTS=sorts, HRS100=hrs100, SP=sp,
        EFF=eff, GSM=gsm, GMM=gm_m,
        METER=meter, KGLOOM=kg_loom, OZSY=ozs_yds
    )

# ══════════════════ APP ══════════════════════
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("DD-DORNIER-CALCULATION  v1.2")
        self.configure(bg=BG_DARK)
        self.minsize(980, 720)
        self.resizable(True, True)

        # fonts
        self.F_TITLE  = tkfont.Font(family="Helvetica", size=17, weight="bold")
        self.F_BOLD   = tkfont.Font(family="Helvetica", size=10, weight="bold")
        self.F_NORM   = tkfont.Font(family="Helvetica", size=9)
        self.F_MONO   = tkfont.Font(family="Consolas",  size=11)
        self.F_BIG    = tkfont.Font(family="Consolas",  size=13, weight="bold")
        self.F_TINY   = tkfont.Font(family="Helvetica", size=8)

        self._last_result = {}
        self._ready = False          # guard: don't calc until UI is built

        self._ttk_style()
        self._ui_header()
        self._ui_inputs()
        self._ui_buttons()
        self._ui_results()
        self._ui_statusbar()

        self._ready = True
        self.after(50, self._recalc)   # first calc after mainloop starts

    # ── ttk style ──────────────────────────────────────
    def _ttk_style(self):
        s = ttk.Style()
        s.theme_use("clam")
        s.configure("TCombobox",
                    fieldbackground=ENTRY_BG, background=ENTRY_BG,
                    foreground=ENTRY_FG, selectbackground=GOLD,
                    selectforeground=BG_DARK, arrowcolor=CYAN,
                    bordercolor=CYAN, lightcolor=CYAN, darkcolor=CYAN)
        s.map("TCombobox",
              fieldbackground=[("readonly", ENTRY_BG)],
              foreground=[("readonly", ENTRY_FG)])

    # ── header ─────────────────────────────────────────
    def _ui_header(self):
        f = tk.Frame(self, bg="#08111E", pady=10)
        f.pack(fill=tk.X)
        tk.Label(f, text="⚙  DD-DORNIER-CALCULATION",
                 font=self.F_TITLE, bg="#08111E", fg=GOLD
                 ).pack(side=tk.LEFT, padx=18)
        tk.Label(f, text="Dornier Loom Production Calculator",
                 font=self.F_BOLD, bg="#08111E", fg=LIGHT
                 ).pack(side=tk.LEFT)
        self._clock_sv = tk.StringVar()
        tk.Label(f, textvariable=self._clock_sv,
                 font=self.F_BOLD, bg="#08111E", fg=CYAN
                 ).pack(side=tk.RIGHT, padx=18)
        self._tick()
        tk.Frame(self, bg=GOLD, height=2).pack(fill=tk.X)

    def _tick(self):
        self._clock_sv.set(datetime.now().strftime("🕐  %d-%b-%Y   %H:%M:%S"))
        self.after(1000, self._tick)

    # ── inputs ─────────────────────────────────────────
    def _ui_inputs(self):
        outer = tk.Frame(self, bg=BG_DARK, pady=8)
        outer.pack(fill=tk.X, padx=18)
        tk.Label(outer, text="▌ INPUT PARAMETERS",
                 font=self.F_BOLD, bg=BG_DARK, fg=ORANGE
                 ).pack(anchor=tk.W, pady=(0,4))

        card = tk.Frame(outer, bg=BG_MID,
                        highlightbackground=CYAN, highlightthickness=1)
        card.pack(fill=tk.X)
        g = tk.Frame(card, bg=BG_MID, padx=14, pady=12)
        g.pack(fill=tk.X)

        # helper: labelled entry
        def lbl(parent, text, r, c, cs=1):
            tk.Label(parent, text=text, font=self.F_BOLD,
                     bg=BG_MID, fg=CYAN
                     ).grid(row=r, column=c, columnspan=cs,
                            sticky=tk.W, pady=(4,1))

        def entry(parent, sv, r, c, w=15):
            e = tk.Entry(parent, textvariable=sv,
                         font=self.F_MONO, bg=ENTRY_BG, fg=ENTRY_FG,
                         insertbackground=GOLD, relief=tk.FLAT,
                         highlightbackground=CYAN, highlightthickness=1,
                         width=w)
            e.grid(row=r, column=c, sticky=tk.W, padx=(0,18), pady=(0,8))
            return e

        # row 0-1: QUALITY (wide)
        lbl(g, 'QUALITY   (e.g.  54.0"-9.30 OZS/40" - 11 X 11)', 0, 0, cs=8)
        self._sv_quality = tk.StringVar(value='54.0"-9.30 OZS/40" - 11 X 11')
        entry(g, self._sv_quality, 1, 0, w=50).grid(
            row=1, column=0, columnspan=5, sticky=tk.W, padx=(0,18), pady=(0,8))

        self._sv_sorts = tk.StringVar(value="✔  Sorts = 11")
        tk.Label(g, textvariable=self._sv_sorts,
                 font=self.F_BOLD, bg=BG_MID, fg=PINK
                 ).grid(row=1, column=5, sticky=tk.W, padx=10)

        # row 2-3: RPM | LOOM DIFF | OZS
        lbl(g, "AVG RPM",              2, 0)
        lbl(g, "LOOM DIFF / K-Picks",  2, 2)
        lbl(g, 'OZS  (per 40")',        2, 4)

        self._sv_rpm  = tk.StringVar(value="190")
        self._sv_diff = tk.StringVar(value="57")
        self._sv_ozs  = tk.StringVar(value="9.3")
        entry(g, self._sv_rpm,  3, 0)
        entry(g, self._sv_diff, 3, 2)
        entry(g, self._sv_ozs,  3, 4)

        # row 4-5: WIDTH | SORTING PINION
        lbl(g, "WIDTH  (inches)",        4, 0)
        lbl(g, "SORTING PINION  (0–10)", 4, 2)

        self._sv_width = tk.StringVar(value="54")
        entry(g, self._sv_width, 5, 0)

        self._sv_sp = tk.IntVar(value=2)
        sp_frame = tk.Frame(g, bg=BG_MID)
        sp_frame.grid(row=5, column=2, columnspan=5, sticky=tk.W)

        self._combo_sp = ttk.Combobox(
            sp_frame, textvariable=self._sv_sp,
            values=list(range(11)), width=7,
            font=self.F_MONO, state="readonly")
        self._combo_sp.pack(side=tk.LEFT)

        self._sv_sp_formula = tk.StringVar()
        tk.Label(sp_frame, textvariable=self._sv_sp_formula,
                 font=self.F_BOLD, bg=BG_MID, fg=GREEN
                 ).pack(side=tk.LEFT, padx=14)

        for c in range(6):
            g.columnconfigure(c, minsize=130)

        # ── bind ALL inputs to _on_change ──────────────
        for sv in (self._sv_quality, self._sv_rpm, self._sv_diff,
                   self._sv_ozs, self._sv_width):
            sv.trace_add("write", self._on_change)

        self._combo_sp.bind("<<ComboboxSelected>>", self._on_change)

    # ── buttons ────────────────────────────────────────
    def _ui_buttons(self):
        f = tk.Frame(self, bg=BG_DARK, pady=8)
        f.pack(fill=tk.X, padx=18)
        cfg = dict(font=self.F_BOLD, relief=tk.FLAT,
                   cursor="hand2", padx=24, pady=9, bd=0)
        tk.Button(f, text="⚡  CALCULATE",
                  bg=BTN_CALC, fg=WHITE,
                  activebackground="#FF8C00", activeforeground=WHITE,
                  command=self._recalc, **cfg).pack(side=tk.LEFT, padx=(0,10))
        tk.Button(f, text="↺  RESET",
                  bg=BTN_RESET, fg=WHITE,
                  activebackground="#FF1493", activeforeground=WHITE,
                  command=self._reset, **cfg).pack(side=tk.LEFT, padx=(0,10))
        tk.Button(f, text="📋  FINAL REPORT",
                  bg=BTN_RPT, fg=WHITE,
                  activebackground="#228B22", activeforeground=WHITE,
                  command=self._report, **cfg).pack(side=tk.LEFT, padx=(0,10))
        tk.Button(f, text="✖  EXIT",
                  bg="#1A1A2E", fg="#FF4444",
                  activebackground="#FF4444", activeforeground=WHITE,
                  command=self.destroy, **cfg).pack(side=tk.RIGHT)

    # ── results ────────────────────────────────────────
    def _ui_results(self):
        outer = tk.Frame(self, bg=BG_DARK, pady=6)
        outer.pack(fill=tk.BOTH, expand=True, padx=18, pady=(0,8))
        tk.Label(outer, text="▌ CALCULATED RESULTS",
                 font=self.F_BOLD, bg=BG_DARK, fg=ORANGE
                 ).pack(anchor=tk.W, pady=(0,5))

        border = tk.Frame(outer, bg=BG_MID,
                          highlightbackground=GOLD, highlightthickness=1)
        border.pack(fill=tk.BOTH, expand=True)

        inner = tk.Frame(border, bg=BG_MID, padx=14, pady=12)
        inner.pack(fill=tk.BOTH, expand=True)

        # 8 result boxes — key matches what _recalc writes
        BOX_DEFS = [
            ("8HRS\n100%",     "HRS100", CYAN),
            ("SORTING\nPINION","SP",     PINK),
            ("EFF %",          "EFF",    GOLD),
            ("GSM",            "GSM",    "#7FFF00"),
            ("GM/METER",       "GMM",    ORANGE),
            ("METER",          "METER",  "#00BFFF"),
            ("KG/LOOM",        "KGLOOM", GREEN),
            ("OZS/YDS",        "OZSY",   "#FF69B4"),
        ]

        self._rv = {}   # key → StringVar

        for col, (label, key, colour) in enumerate(BOX_DEFS):
            inner.columnconfigure(col, weight=1)
            box = tk.Frame(inner, bg=BG_CARD,
                           highlightbackground=colour, highlightthickness=2)
            box.grid(row=0, column=col, padx=5, pady=5, sticky=tk.NSEW)

            tk.Label(box, text=label, font=self.F_TINY,
                     bg=BG_CARD, fg=colour, wraplength=100
                     ).pack(pady=(8,2))

            sv = tk.StringVar(value="—")
            tk.Label(box, textvariable=sv,
                     font=self.F_BIG, bg=BG_CARD, fg=WHITE,
                     wraplength=110
                     ).pack(pady=(0,8))

            self._rv[key] = sv   # safe: dict complete before _ready=True

        # SP formula label
        self._sv_sp_explain = tk.StringVar(value="")
        tk.Label(inner, textvariable=self._sv_sp_explain,
                 font=self.F_BOLD, bg=BG_MID, fg=PINK
                 ).grid(row=1, column=0, columnspan=8,
                        sticky=tk.W, pady=(6,2), padx=4)



    # ── status bar ─────────────────────────────────────
    def _ui_statusbar(self):
        tk.Frame(self, bg=GOLD, height=1).pack(fill=tk.X)
        self._sv_status = tk.StringVar(
            value="Ready — results update live as you type")
        tk.Label(self, textvariable=self._sv_status,
                 font=self.F_TINY, bg="#08111E", fg=LIGHT,
                 anchor=tk.W, pady=4
                 ).pack(fill=tk.X, padx=12)

    # ── event: any input changed ────────────────────────
    def _on_change(self, *_):
        if self._ready:
            self._recalc(silent=True)

    # ── core recalculate ───────────────────────────────
    def _recalc(self, silent=False):
        if not self._ready:
            return

        quality = self._sv_quality.get().strip()

        # update sorts label
        sorts = parse_sorts(quality)
        self._sv_sorts.set(f"✔  Sorts = {sorts}" if sorts
                           else "⚠  Sorts not found")

        # update SP formula preview
        try:
            sp_val = int(self._sv_sp.get())
        except Exception:
            sp_val = 0

        if sorts:
            sp_preview = ((sorts * 4) - sp_val) * 10
            self._sv_sp_formula.set(
                f"(({sorts}×4)−{sp_val})×10  =  {sp_preview}")
        else:
            self._sv_sp_formula.set("")

        # full calculation
        try:
            rpm      = float(self._sv_rpm.get())
            loom_diff= float(self._sv_diff.get())
            ozs      = float(self._sv_ozs.get())
            width    = float(self._sv_width.get())

            if rpm <= 0 or ozs <= 0 or width <= 0:
                raise ValueError("RPM, OZS and WIDTH must be > 0")

            r = dornier_calc(quality, rpm, loom_diff, ozs, width, sp_val)
            self._last_result = r
            self._last_result["_in"] = dict(
                QUALITY=quality, RPM=rpm, DIFF=loom_diff,
                OZS=ozs, WIDTH=width, SP_VAL=sp_val)

            # push to boxes  ← key names MUST match BOX_DEFS above
            self._rv["HRS100"].set(f"{r['HRS100']:,.0f}")
            self._rv["SP"    ].set(f"{r['SP']:,}")
            self._rv["EFF"   ].set(f"{r['EFF']:.2f}")
            self._rv["GSM"   ].set(f"{r['GSM']:.2f}")
            self._rv["GMM"   ].set(f"{r['GMM']:.2f}")
            self._rv["METER" ].set(f"{r['METER']:.2f}")
            self._rv["KGLOOM"].set(f"{r['KGLOOM']:.2f}")
            self._rv["OZSY"  ].set(f"{r['OZSY']:.3f}")

            self._sv_sp_explain.set(
                f"  ⚙  Sorting Pinion :  "
                f"(({r['SORTS']}×4) − {sp_val}) × 10  =  {r['SP']}")

            self._sv_status.set(
                f"✔  {datetime.now().strftime('%H:%M:%S')}  │  "
                f"EFF: {r['EFF']:.2f}%   "
                f"KG/LOOM: {r['KGLOOM']:.2f} kg   "
                f"METER: {r['METER']:.2f} m   "
                f"GSM: {r['GSM']:.2f}")

        except Exception as exc:
            self._sv_status.set(f"⚠  {exc}")
            if not silent:
                messagebox.showerror("Input Error", str(exc))

    # ── reset ──────────────────────────────────────────
    def _reset(self):
        self._ready = False   # pause traces
        self._sv_quality.set('54.0"-9.30 OZS/40" - 11 X 11')
        self._sv_rpm.set("190")
        self._sv_diff.set("57")
        self._sv_ozs.set("9.3")
        self._sv_width.set("54")
        self._sv_sp.set(2)
        self._last_result = {}
        for sv in self._rv.values():
            sv.set("—")
        self._sv_sp_explain.set("")
        self._sv_status.set("Reset complete")
        self._ready = True
        self.after(50, self._recalc)

    # ── final report window ────────────────────────────
    def _report(self):
        if not self._last_result or "_in" not in self._last_result:
            messagebox.showwarning("No Data", "Press ⚡ CALCULATE first.")
            return

        r   = self._last_result
        inp = r["_in"]
        now = datetime.now().strftime("%d-%b-%Y  %H:%M:%S")

        win = tk.Toplevel(self)
        win.title("📋  DORNIER FINAL REPORT")
        win.configure(bg=BG_DARK)
        win.minsize(680, 620)
        win.resizable(True, True)

        # header
        hf = tk.Frame(win, bg="#08111E", pady=10)
        hf.pack(fill=tk.X)
        tk.Label(hf,
                 text="╔══  DD-DORNIER-CALCULATION  ─  FINAL REPORT  ══╗",
                 font=tkfont.Font(family="Consolas", size=13, weight="bold"),
                 bg="#08111E", fg=GOLD).pack()
        tk.Label(hf, text=f"Generated : {now}",
                 font=tkfont.Font(family="Consolas", size=9),
                 bg="#08111E", fg=LIGHT).pack()
        tk.Frame(win, bg=GOLD, height=2).pack(fill=tk.X)

        body = tk.Frame(win, bg=BG_DARK, padx=22, pady=14)
        body.pack(fill=tk.BOTH, expand=True)

        CF = tkfont.Font(family="Consolas", size=11, weight="bold")
        CV = tkfont.Font(family="Consolas", size=11)
        CH = tkfont.Font(family="Helvetica", size=10, weight="bold")

        def sec(title):
            tk.Label(body, text=title, font=CH,
                     bg=BG_DARK, fg=ORANGE).pack(anchor=tk.W, pady=(10,4))

        def row(label, value, lc=CYAN, vc=WHITE, i=0):
            bg = BG_MID if i % 2 == 0 else BG_CARD
            f = tk.Frame(body, bg=bg)
            f.pack(fill=tk.X, pady=1)
            tk.Label(f, text=label, width=24, anchor=tk.W,
                     font=CF, bg=bg, fg=lc).pack(side=tk.LEFT, padx=(6,0))
            tk.Label(f, text=value, anchor=tk.W,
                     font=CV, bg=bg, fg=vc).pack(side=tk.LEFT, padx=10)

        sec("INPUT PARAMETERS")
        in_rows = [
            ("QUALITY",          inp["QUALITY"]),
            ("AVG RPM",          f"{inp['RPM']:.0f}"),
            ("8HRS_100%",        f"{r['HRS100']:,.0f}"),
            ("LOOM DIFF",        f"{inp['DIFF']:.0f}"),
            ('OZS / 40"',        f"{inp['OZS']}"),
            ("WIDTH (inches)",   f'{inp["WIDTH"]:.0f}"'),
            ("SORTING PINION",   f"{r['SP']}"),
        ]
        for i,(l,v) in enumerate(in_rows):
            vc = GREEN if l in ("8HRS_100%","SORTING PINION") else WHITE
            row(l, v, CYAN, vc, i)

        sec("CALCULATED RESULTS")
        out_rows = [
            ("EFF %",      f"{r['EFF']:.2f} %"),
            ("GSM",        f"{r['GSM']:.2f}"),
            ("GM / METER", f"{r['GMM']:.4f} g"),
            ("METER",      f"{r['METER']:.4f} m"),
            ("KG / LOOM",  f"{r['KGLOOM']:.4f} kg"),
            ("OZS / YDS",  f"{r['OZSY']:.4f}"),
        ]
        for i,(l,v) in enumerate(out_rows):
            vc = GREEN if l in ("EFF %","METER","KG / LOOM") else WHITE
            row(l, v, GOLD, vc, i)

        tk.Label(body,
                 text=(f"\n  ⚙  Sorting Pinion Formula:  "
                       f"(({r['SORTS']}×4) − {inp['SP_VAL']}) × 10  =  {r['SP']}"),
                 font=tkfont.Font(family="Consolas", size=11, weight="bold"),
                 bg=BG_DARK, fg=PINK).pack(anchor=tk.W)

        tk.Frame(win, bg=GOLD, height=2).pack(fill=tk.X)
        tk.Label(win,
                 text="DD-DORNIER-CALCULATION",
                 font=tkfont.Font(family="Helvetica", size=8),
                 bg="#08111E", fg=LIGHT, pady=4).pack(fill=tk.X)
        tk.Button(win, text="✖  CLOSE",
                  bg=BTN_RESET, fg=WHITE,
                  font=tkfont.Font(family="Helvetica", size=9, weight="bold"),
                  relief=tk.FLAT, padx=14, pady=6, cursor="hand2",
                  command=win.destroy).pack(pady=8)


# ══════════════════ ENTRY POINT ══════════════
if __name__ == "__main__":
    App().mainloop()
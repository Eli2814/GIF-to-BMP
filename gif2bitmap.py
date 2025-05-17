import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageSequence

def gif_to_bitmaps(gif_path, width, height, threshold):
    img = Image.open(gif_path)
    frames = []
    for frame in ImageSequence.Iterator(img):
        bmp = frame.convert('L')\
                   .resize((width, height), Image.NEAREST)
        bw = bmp.point(lambda x: 0 if x < threshold else 1, '1')
        frames.append(bw)
    return frames

def bitmap_to_c_array(frames, width, height, prefix):
    lines = [f"// Generated from GIF: {len(frames)} frames, size {width}x{height}"]
    for idx, frame in enumerate(frames):
        name = f"{prefix}{idx}"
        lines.append(f"const uint8_t {name}[] PROGMEM = {{")
        for y in range(height):
            row_bits = []
            byte = 0
            for x in range(width):
                bit = 1 if frame.getpixel((x, y)) else 0
                byte |= (bit << (7 - (x % 8)))
                if (x % 8 == 7) or (x == width - 1):
                    row_bits.append(f"0b{byte:08b}")
                    byte = 0
            comma = "," if y < height - 1 else ""
            lines.append("  " + ", ".join(row_bits) + comma)
        lines.append("};\n")
    ptrs = ", ".join([f"{prefix}{i}" for i in range(len(frames))])
    lines.append(f"const uint8_t* const {prefix}List[] PROGMEM = {{{ptrs}}};")
    lines.append(f"const uint8_t {prefix}Count = {len(frames)};")
    return "\n".join(lines)

class Gif2HeaderApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("GIF → Arduino Header")
        self.geometry("560x260")

        # Input GIF
        tk.Label(self, text="Input GIF:").grid(row=0, column=0, sticky="e", padx=4, pady=4)
        self.gif_path = tk.Entry(self, width=45)
        self.gif_path.grid(row=0, column=1, padx=4, pady=4)
        tk.Button(self, text="Browse…", command=self.browse_gif).grid(row=0, column=2)

        # Output .h
        tk.Label(self, text="Output .h:").grid(row=1, column=0, sticky="e", padx=4, pady=4)
        self.out_path = tk.Entry(self, width=45)
        self.out_path.grid(row=1, column=1, padx=4, pady=4)
        tk.Button(self, text="Browse…", command=self.browse_output).grid(row=1, column=2)

        # Width & Height
        tk.Label(self, text="Width:").grid(row=2, column=0, sticky="e", padx=4)
        self.width_var = tk.IntVar(value=128)
        tk.Entry(self, textvariable=self.width_var, width=6).grid(row=2, column=1, sticky="w")
        tk.Label(self, text="Height:").grid(row=2, column=1, sticky="e", padx=(0,60))
        self.height_var = tk.IntVar(value=32)
        tk.Entry(self, textvariable=self.height_var, width=6).grid(row=2, column=2, sticky="w")

        # Threshold
        tk.Label(self, text="Threshold:").grid(row=3, column=0, sticky="e", padx=4, pady=4)
        self.thresh_var = tk.IntVar(value=128)
        tk.Entry(self, textvariable=self.thresh_var, width=6).grid(row=3, column=1, sticky="w")

        # Array name prefix
        tk.Label(self, text="Array Prefix:").grid(row=4, column=0, sticky="e", padx=4)
        self.prefix_var = tk.StringVar(value="frame")
        tk.Entry(self, textvariable=self.prefix_var, width=12).grid(row=4, column=1, sticky="w")

        # Convert button
        tk.Button(self, text="Convert", command=self.convert).grid(row=5, column=1, pady=10)

    def browse_gif(self):
        path = filedialog.askopenfilename(filetypes=[("GIF Files","*.gif")])
        if path:
            self.gif_path.delete(0, tk.END)
            self.gif_path.insert(0, path)

    def browse_output(self):
        path = filedialog.asksaveasfilename(defaultextension=".h", filetypes=[("Header Files","*.h")])
        if path:
            self.out_path.delete(0, tk.END)
            self.out_path.insert(0, path)

    def convert(self):
        gif = self.gif_path.get().strip()
        out = self.out_path.get().strip()
        w, h = self.width_var.get(), self.height_var.get()
        t = self.thresh_var.get()
        prefix = self.prefix_var.get().strip()

        if not gif or not out:
            messagebox.showerror("Error", "Please choose both an input GIF and an output header file.")
            return

        try:
            frames = gif_to_bitmaps(gif, w, h, t)
            code = bitmap_to_c_array(frames, w, h, prefix)
            with open(out, "w") as f:
                f.write(code)
            messagebox.showinfo("Success", f"Generated {len(frames)} frames in:\n{out}")
        except Exception as e:
            messagebox.showerror("Error", str(e))


if __name__ == "__main__":
    app = Gif2HeaderApp()
    app.mainloop() 
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image
from pdf2image import convert_from_path
import os
from PyPDF2 import PdfMerger, PdfReader, PdfWriter
import fitz  
from ttkbootstrap import Style
from ttkbootstrap.widgets import Scale


# === Image(s) to PDF ===
def convert_images_to_pdf():
    file_paths = filedialog.askopenfilenames(
        title="Select image(s)",
        filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.tiff *.webp")]
    )

    if not file_paths:
        return

    try:
        images = []
        for path in file_paths:
            img = Image.open(path)
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")
            images.append(img)

        save_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            title="Save PDF As"
        )

        if save_path:
            if len(images) == 1:
                images[0].save(save_path, "PDF")
            else:
                images[0].save(save_path, save_all=True, append_images=images[1:])
            messagebox.showinfo("Success", f"PDF saved to:\n{save_path}")

    except Exception as e:
        messagebox.showerror("Error", f"Failed to convert image(s):\n{e}")

# === PDF to Image(s) ===
def convert_pdf_to_images():
    pdf_path = filedialog.askopenfilename(
        title="Select a PDF file",
        filetypes=[("PDF files", "*.pdf")]
    )

    if not pdf_path:
        return

    try:
        output_folder = filedialog.askdirectory(title="Select folder to save images")
        if not output_folder:
            return

        images = convert_from_path(pdf_path)

        base_name = os.path.splitext(os.path.basename(pdf_path))[0]

        for i, img in enumerate(images):
            filename = f"{base_name}_page_{i + 1}.jpg"
            full_path = os.path.join(output_folder, filename)
            img.save(full_path, "JPEG")

        messagebox.showinfo("Success", f"{len(images)} page(s) saved as images in:\n{output_folder}")

    except Exception as e:
        messagebox.showerror("Error", f"Failed to convert PDF:\n{e}")



def merge_pdfs():
    pdf_paths = filedialog.askopenfilenames(
        title="select PDF files",
        filetypes=[("PDF files", "*.pdf")]
    )

    if not pdf_paths or len(pdf_paths) < 2:
        messagebox.showwarning("Warning", "Select atleast two files")
        return
    
    # Get name of first selected file (without folder and extension)
    first_file_name = os.path.splitext(os.path.basename(pdf_paths[0]))[0]
    default_filename = f"{first_file_name}_merged.pdf"

    save_path = filedialog.asksaveasfilename(
        defaultextension=".pdf",
        initialfile=default_filename,
        filetypes=[("PDF files", "*.pdf")],
        title="Save Merged PDF As"
    )


    if not save_path:
       return
    
    try:
        merger = PdfMerger()
        for path in pdf_paths:
            merger.append(path)
        merger.write(save_path)
        merger.close()

        messagebox.showinfo("Success", f"Merged PDF saved at: \n{save_path}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to merge PDFs at:\n{save_path}")

def split_pdf():
    pdf_path = filedialog.askopenfilename(
        title="Select a PDF to split",
        filetypes=[("PDF files", "*.pdf")]
    )

    if not pdf_path:
      return
    
    output_folder = filedialog.askdirectory(
        title="Select Folder to save split pages"
    )

    if not output_folder:
        return 
    
    try:
        reader = PdfReader(pdf_path)
        for i, page in enumerate(reader.pages):
            writer = PdfWriter()
            writer.add_page(page)

            output_filename = os.path.join(output_folder, f"page_{i+1}.pdf")
            with open(output_filename, "wb") as output_pdf:
                writer.write(output_pdf)

        messagebox.showinfo("Success", f"PDF split into {len(reader.pages)} pages in:\n{output_folder}")

    except Exception as e:
        messagebox.showerror("Error", f"Failed to split PDF:\n{e}")

def encrypt_pdf():
    pdf_path = filedialog.askopenfilename(
        title="Select PDF to Password-Protect",
        filetypes=[("PDF files", "*.pdf")]
    )

    if not pdf_path:
        return

    # Ask for password twice
    password1 = simpledialog.askstring("Set Password", "Enter password for the PDF:")
    password2 = simpledialog.askstring("Confirm Password", "Re-enter the password:")

    if not password1 or not password2:
        messagebox.showwarning("Cancelled", "Password not set.")
        return

    if password1 != password2:
        messagebox.showerror("Mismatch", "Passwords do not match.")
        return

    try:
        reader = PdfReader(pdf_path)
        writer = PdfWriter()

        for page in reader.pages:
            writer.add_page(page)

        writer.encrypt(password1)

        # Auto-generate default filename with "_protected"
        base_name = os.path.splitext(os.path.basename(pdf_path))[0]
        default_filename = f"{base_name}_protected.pdf"

        save_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            initialfile=default_filename,
            filetypes=[("PDF files", "*.pdf")],
            title="Save Encrypted PDF As"
        )

        if save_path:
            with open(save_path, "wb") as f:
                writer.write(f)
            messagebox.showinfo("Success", f"PDF protected with password:\n{save_path}")

    except Exception as e:
        messagebox.showerror("Error", f"Failed to encrypt PDF:\n{e}")

def decrypt_pdf():
    pdf_path = filedialog.askopenfilename(
        title="Select a password-protected PDF",
        filetypes=[("PDF files", "*.pdf")]
    )

    if not pdf_path:
        return

    password = simpledialog.askstring("PDF Password", "Enter the password:")

    if not password:
        messagebox.showwarning("Cancelled", "Password not entered.")
        return

    try:
        reader = PdfReader(pdf_path)

        if not reader.is_encrypted:
            messagebox.showinfo("Info", "This PDF is not password-protected.")
            return

        if not reader.decrypt(password):
            messagebox.showerror("Error", "Incorrect password.")
            return

        writer = PdfWriter()

        for page in reader.pages:
            writer.add_page(page)

        # Suggest output name like: file_decrypted.pdf
        base_name = os.path.splitext(os.path.basename(pdf_path))[0]
        default_filename = f"{base_name}_decrypted.pdf"

        save_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            initialfile=default_filename,
            filetypes=[("PDF files", "*.pdf")],
            title="Save Decrypted PDF As"
        )

        if save_path:
            with open(save_path, "wb") as f:
                writer.write(f)
            messagebox.showinfo("Success", f"Password removed and saved to:\n{save_path}")

    except Exception as e:
        messagebox.showerror("Error", f"Failed to decrypt PDF:\n{e}")


def compress_pdf_with_quality():
    pdf_path = filedialog.askopenfilename(
        title="Select PDF to Compress",
        filetypes=[("PDF files", "*.pdf")]
    )
    if not pdf_path:
        return

    try:
        level = compression_level.get()

        # Convert level (1–10) to zoom scale (0.8–2.0 range)
        zoom_scale = 0.6 + (level / 10 * 1.4)  # 1 → 0.74x | 10 → 2.0x

        doc = fitz.open(pdf_path)
        new_doc = fitz.open()

        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            pix = page.get_pixmap(matrix=fitz.Matrix(zoom_scale, zoom_scale))
            img_pdf = fitz.open()
            img_pdf.insert_page(
                0,
                width=pix.width,
                height=pix.height
            )
            img_page = img_pdf[0]
            img_page.insert_image(
                fitz.Rect(0, 0, pix.width, pix.height),
                pixmap=pix
            )
            new_doc.insert_pdf(img_pdf)

        base_name = os.path.splitext(os.path.basename(pdf_path))[0]
        default_filename = f"{base_name}_compressed.pdf"

        save_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            initialfile=default_filename,
            filetypes=[("PDF files", "*.pdf")],
            title="Save Compressed PDF As"
        )

        if save_path:
            new_doc.save(save_path, deflate=True)
            new_doc.close()
            messagebox.showinfo("Success", f"Compressed PDF saved to:\n{save_path}")

    except Exception as e:
        messagebox.showerror("Error", f"Compression failed:\n{e}")



# === GUI Window ===
root = tk.Tk()
root.title("Local PDF")
root.geometry("420x560")
root.config(bg="#F7F7F7")  # Light gray background


button_style = {
    "font": ("Arial", 11),
    "width": 20,
    "height": 2,
    "bg": "#2D89EF",  # Clean blue
    "fg": "white",    # White text
    "activebackground": "#1B5EAB",  # Darker blue when clicked
    "activeforeground": "white",   # White text when clicked
    "bd": 0  # Borderless button
}

style = Style("flatly")  # You can also try "cosmo", "solar", etc.
compression_level = tk.IntVar(value=7)  # Default: Medium-High quality


tk.Label(root, text="Local PDF", font=("Arial", 14)).pack(pady=15)

tk.Button(root, text="Image to PDF", command=convert_images_to_pdf, **button_style).pack(pady=10)
tk.Button(root, text="PDF to Images", command=convert_pdf_to_images, **button_style).pack(pady=10)
tk.Button(root, text="Merge PDFs", command=merge_pdfs, **button_style).pack(pady=10)
tk.Button(root, text="Split PDF", command=split_pdf, **button_style).pack(pady=10)
tk.Button(root, text="Encrypt PDF", command=encrypt_pdf, **button_style).pack(pady=10)
tk.Button(root, text="Remove PDF Password", command=decrypt_pdf, **button_style).pack(pady=10)

tk.Label(root, text="Compression Quality (1 = Max compression, 10 = Best quality)",
         font=("Arial", 10), fg="navy").pack()
frame_slider = tk.Frame(root, bg="#F7F7F7")  # Wrapper frame for horizontal layout
frame_slider.pack(pady=5)

tk.Label(frame_slider, text="1", font=("Arial", 9), bg="#F7F7F7").pack(side="left", padx=(10, 0))

slider = Scale(frame_slider,
               from_=1,
               to=10,
               orient="horizontal",
               variable=compression_level,
               length=200,
               bootstyle="info")
slider.pack(side="left", padx=5)

tk.Label(frame_slider, text="10", font=("Arial", 9), bg="#F7F7F7").pack(side="left", padx=(0, 10))


tk.Button(root, text="Compress PDF", command=compress_pdf_with_quality, **button_style).pack(pady=10)




root.mainloop()

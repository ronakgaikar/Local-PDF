import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image
from pdf2image import convert_from_path
import os
from PyPDF2 import PdfMerger

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
    
    save_path = filedialog.asksaveasfilename(
        defaultextension=".pdf",
        filetypes= [("PDF files", ".pdf")],
        title="save merged pdf as"
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

# === GUI Window ===
root = tk.Tk()
root.title("Smart PDF Tool")
root.geometry("420x260")

tk.Label(root, text="Local PDF", font=("Arial", 14)).pack(pady=15)

tk.Button(root, text="Image to PDF", font=("Arial", 11),
          command=convert_images_to_pdf).pack(pady=10)

tk.Button(root, text="PDF to Images", font=("Arial", 11),
          command=convert_pdf_to_images).pack(pady=10)

tk.Button(root, text="Merge PDFs", font=("Arial", 11),
          command=merge_pdfs).pack(pady=10)

root.mainloop()

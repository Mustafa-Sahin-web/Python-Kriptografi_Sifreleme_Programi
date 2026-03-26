import os, sys, time, hashlib, random, secrets, traceback
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image

# ================= GLOBAL CRASH GUARD =================
def global_exception_handler(exctype, value, tb):
    print("KRİTİK HATA:\n", "".join(traceback.format_exception(exctype, value, tb)))

sys.excepthook = global_exception_handler

# ================= KRİPTO MOTORU =================
try:
    from argon2.low_level import hash_secret_raw, Type
    from cryptography.hazmat.primitives.kdf.hkdf import HKDF
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    ENGINE_NAME = "AES-256-GCM + ARGON2ID + HKDF"
except Exception as e:
    print("Kütüphane Hatası:", e)
    sys.exit()

# ================= ANAHTAR TÜRETME =================
def keys_uret(parola, salt):
    master = hash_secret_raw(
        secret=parola.encode(),
        salt=salt,
        time_cost=3,
        memory_cost=64*1024,
        parallelism=2,
        hash_len=32,
        type=Type.ID
    )
    # Buradaki hizalamaya dikkat: hkdf, fonksiyonun içinde (bir tab içerde) olmalı
    hkdf = HKDF(
        algorithm=hashes.SHA256(),
        length=64,
        salt=None,
        info=b"Ultra Sifreleme"  # Burayı değiştirdiğin için eski mühürleri açamazsın!
    )
    derived = hkdf.derive(master)
    return derived[:32], derived[32:]

# ================= BIT UTIL =================
def bytes_to_bits(data):
    return ''.join(f'{b:08b}' for b in data)

def bits_to_bytes(bit_str):
    usable = len(bit_str) - (len(bit_str) % 8)
    bit_str = bit_str[:usable]
    return bytes(int(bit_str[i:i+8],2) for i in range(0,usable,8))

# ================= LSB CORE =================
def write_bits(px, bits, start_bit, order=None):
    px = px[:]
    for i, bit in enumerate(bits):
        bit_index = start_bit + i
        pixel_index = bit_index // 3
        channel = bit_index % 3
        if order:
            pixel_index = order[pixel_index]
        p = list(px[pixel_index])
        p[channel] = (p[channel] & ~1) | int(bit)
        px[pixel_index] = tuple(p)
    return px

def read_bits(px, count, start_bit, order=None):
    bits = []
    for i in range(count):
        bit_index = start_bit + i
        pixel_index = bit_index // 3
        channel = bit_index % 3
        if order:
            pixel_index = order[pixel_index]
        bits.append(str(px[pixel_index][channel] & 1))
    return ''.join(bits)

# ================= CORE LOGIC =================
def mahser_muhurle():
    try:
        mesaj = txt_mesaj.get("1.0", tk.END).strip()
        parola = ent_parola.get()
        if not mesaj or not parola or not secilen_yol:
            messagebox.showwarning("Eksik Veri", "Görsel, mesaj ve parola gereklidir.")
            return

        log("Şifreleme başlatıldı...", "orange")
        img = Image.open(secilen_yol).convert("RGB")
        px = list(img.getdata())
        salt = secrets.token_bytes(16)
        enc_key, stego_key = keys_uret(parola, salt)
        cipher = AESGCM(enc_key)
        nonce = secrets.token_bytes(12)
        ciphertext = cipher.encrypt(nonce, mesaj.encode(), None)

        magic = b"MH19"
        payload = magic + nonce + ciphertext
        header = len(payload).to_bytes(4, "big")
        salt_bits = bytes_to_bits(salt)
        data_bits = bytes_to_bits(header + payload)

        if len(salt_bits) + len(data_bits) > len(px)*3:
            messagebox.showerror("Hata", "Görsel kapasitesi yetersiz.")
            return

        new_px = write_bits(px, salt_bits, 0)
        seed = int.from_bytes(hashlib.sha256(stego_key).digest(), "big")
        rng = random.Random(seed)
        order = list(range(len(px))); rng.shuffle(order)
        new_px = write_bits(new_px, data_bits, 128, order)

        img.putdata(new_px)
        save_dir = os.path.join(os.environ['USERPROFILE'], 'Downloads')
        path = os.path.join(save_dir, f"MUHUR_{int(time.time())}.png")
        img.save(path, "PNG")
        log("MÜHÜRLENDİ ✔", "#00ff00")
        messagebox.showinfo("BAŞARILI", f"Mühürlendi: {os.path.basename(path)}")
    except Exception as e:
        log(f"Hata: {e}", "red")

def mahser_desifre():
    try:
        parola = ent_parola.get()
        if not parola or not secilen_yol:
            messagebox.showwarning("Eksik Veri", "Görsel ve parola gerekli.")
            return

        log("Analiz başlatıldı...", "orange")
        img = Image.open(secilen_yol).convert("RGB")
        px = list(img.getdata())

        salt_bits = read_bits(px, 128, 0)
        salt = bits_to_bytes(salt_bits)
        enc_key, stego_key = keys_uret(parola, salt)

        seed = int.from_bytes(hashlib.sha256(stego_key).digest(), "big")
        rng = random.Random(seed)
        order = list(range(len(px))); rng.shuffle(order)

        header_bits = read_bits(px, 32, 128, order)
        payload_len = int(header_bits, 2)
        if payload_len <= 0 or payload_len > len(px):
            raise Exception("Header bozuk")

        payload_bits = read_bits(px, payload_len*8, 160, order)
        payload = bits_to_bytes(payload_bits)

        if payload[:4] != b"MH19":
            raise Exception("Magic uyuşmuyor")

        nonce = payload[4:16]
        ciphertext = payload[16:]
        cipher = AESGCM(enc_key)
        sonuc = cipher.decrypt(nonce, ciphertext, None).decode()

        txt_mesaj.delete("1.0", tk.END)
        txt_mesaj.insert(tk.END, sonuc)
        log("ERİŞİM ONAYLANDI ✔", "#00ff00")
    except Exception:
        log("ERİŞİM REDDEDİLDİ ✖", "red")

# ================= MODERN GUI =================
root = tk.Tk()
root.title("Kriptografi Programı")
root.geometry("500x880")
root.configure(bg="#0a0a0a")

def log(msg, color="#00ff00"):
    t = time.strftime("%H:%M:%S")
    txt_log.config(state="normal")
    txt_log.insert(tk.END, f"[{t}] {msg}\n", color)
    txt_log.tag_config(color, foreground=color)
    txt_log.config(state="disabled")
    txt_log.see(tk.END)

# Header
header = tk.Frame(root, bg="#0a0a0a")
header.pack(pady=20)
tk.Label(header, text="☪", font=("Arial", 60), bg="#0a0a0a", fg="#ff0000").pack()
tk.Label(header, text="Kriptografi Paneli", font=("Impact", 24), bg="#0a0a0a", fg="white").pack()

secilen_yol = None
def dosya_sec():
    global secilen_yol
    secilen_yol = filedialog.askopenfilename(filetypes=[("PNG Dosyaları", "*.png")])
    if secilen_yol:
        lbl_status.config(text=f"Yüklendi: {os.path.basename(secilen_yol)}", fg="#00ff00")
        log("Görsel katman yüklendi.")

# Step 1: File
file_fr = tk.LabelFrame(root, text=" 1. GÖRSEL KATMAN ", bg="#0a0a0a", fg="#00d4ff", font=("Arial", 8, "bold"), padx=10, pady=10)
file_fr.pack(fill="x", padx=30, pady=10)
tk.Button(file_fr, text="DOSYA SEÇ", command=dosya_sec, bg="#1a1a1a", fg="white", relief="flat", width=20).pack(pady=5)
lbl_status = tk.Label(file_fr, text="Dosya Seçilmedi", bg="#0a0a0a", fg="#555", font=("Arial", 8))
lbl_status.pack()

# Step 2: Message
msg_fr = tk.LabelFrame(root, text=" 2. STRATEJİK VERİ ", bg="#0a0a0a", fg="#00d4ff", font=("Arial", 8, "bold"), padx=10, pady=10)
msg_fr.pack(fill="x", padx=30, pady=10)
txt_mesaj = tk.Text(msg_fr, height=4, bg="#050505", fg="#00ff00", insertbackground="white", relief="flat", font=("Consolas", 10))
txt_mesaj.pack(fill="x")

# Step 3: Password
pass_fr = tk.LabelFrame(root, text=" 3. GÜVENLİK ANAHTARI ", bg="#0a0a0a", fg="#00d4ff", font=("Arial", 8, "bold"), padx=10, pady=10)
pass_fr.pack(fill="x", padx=30, pady=10)
ent_parola = tk.Entry(pass_fr, show="●", bg="#050505", fg="white", insertbackground="white", relief="flat", font=("Arial", 14), justify="center")
ent_parola.pack(fill="x")

# Actions
btn_fr = tk.Frame(root, bg="#0a0a0a")
btn_fr.pack(pady=20)
tk.Button(btn_fr, text="MÜHÜRLE", command=mahser_muhurle, bg="#800000", fg="white", width=15, height=2, font=("Arial", 10, "bold"), relief="flat").pack(side="left", padx=10)
tk.Button(btn_fr, text="DEŞİFRE", command=mahser_desifre, bg="#001a33", fg="white", width=15, height=2, font=("Arial", 10, "bold"), relief="flat").pack(side="left", padx=10)

# Terminal
log_fr = tk.Frame(root, bg="#0a0a0a")
log_fr.pack(fill="both", expand=True, padx=30, pady=10)
txt_log = tk.Text(log_fr, bg="black", fg="#00ff00", font=("Consolas", 8), state="disabled", relief="flat")
txt_log.pack(fill="both", expand=True)

log(f"Sistem Çevrimiçi | Motor: {ENGINE_NAME}")
root.mainloop()
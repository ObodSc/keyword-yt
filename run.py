import re
import time

from yt_dlp import YoutubeDL


# ============================================================
# PENGATURAN
# ============================================================

JUMLAH_KEYWORD = 6

# Berapa banyak hasil pencarian yang akan diperiksa
JUMLAH_HASIL = 30


# ============================================================
# AMBIL VIDEO ID
# ============================================================

def ambil_video_id(link):

    pola = [
        r"(?:youtube\.com/watch\?v=)([^&]+)",
        r"(?:youtu\.be/)([^?&]+)",
        r"(?:youtube\.com/shorts/)([^?&]+)"
    ]

    for p in pola:

        hasil = re.search(p, link)

        if hasil:
            return hasil.group(1)

    return None


# ============================================================
# BERSIHKAN TEKS
# ============================================================

def bersihkan_teks(teks):

    teks = re.sub(r"\([^)]*\)", " ", teks)
    teks = re.sub(r"\[[^\]]*\]", " ", teks)
    teks = re.sub(r"\s+", " ", teks)

    return teks.strip()


# ============================================================
# AMBIL INFORMASI VIDEO
# ============================================================

def ambil_info_video(video_id):

    url = "https://www.youtube.com/watch?v=" + video_id

    print("\nMengambil informasi video...")

    opsi = {
        "quiet": True,
        "no_warnings": True,
        "skip_download": True
    }

    try:

        with YoutubeDL(opsi) as ydl:
            info = ydl.extract_info(url, download=False)

        return {
            "id": video_id,
            "judul": info.get("title", "") or "",
            "channel": (
                info.get("channel")
                or info.get("uploader")
                or ""
            )
        }

    except Exception as e:

        print("\nGagal mengambil informasi video:")
        print(e)

        return None


# ============================================================
# BUAT KANDIDAT KEYWORD
# ============================================================

def buat_keyword(judul, channel):

    hasil = []

    judul = bersihkan_teks(judul)
    channel = bersihkan_teks(channel)

    # 1. Judul lengkap
    if judul:
        hasil.append(judul)

    # 2. Judul + channel
    if judul and channel:
        hasil.append(f"{judul} {channel}")
        hasil.append(f"{channel} {judul}")

    # 3. Judul + song
    if judul:
        hasil.append(f"{judul} song")

    # 4. Judul + channel + song
    if judul and channel:
        hasil.append(f"{judul} {channel} song")
        hasil.append(f"{channel} {judul} song")

    # 5. Potongan 2 kata
    kata = [x for x in judul.split() if len(x) >= 2]

    for i in range(len(kata) - 1):
        hasil.append(f"{kata[i]} {kata[i + 1]}")

    # 6. Potongan 3 kata
    for i in range(len(kata) - 2):
        hasil.append(
            f"{kata[i]} {kata[i + 1]} {kata[i + 2]}"
        )

    # Hapus duplikat
    hasil_bersih = []
    sudah_ada = set()

    for keyword in hasil:

        keyword = keyword.strip()
        kunci = keyword.lower()

        if not keyword:
            continue

        if kunci in sudah_ada:
            continue

        sudah_ada.add(kunci)
        hasil_bersih.append(keyword)

    return hasil_bersih[:JUMLAH_KEYWORD]


# ============================================================
# CARI VIDEO DI HASIL SEARCH
# ============================================================

def cari_posisi(keyword, target_video_id):

    opsi = {
        "quiet": True,
        "no_warnings": True,
        "extract_flat": True,
        "skip_download": True
    }

    try:

        with YoutubeDL(opsi) as ydl:
            hasil = ydl.extract_info(
                f"ytsearch{JUMLAH_HASIL}:{keyword}",
                download=False
            )

        entries = hasil.get("entries", []) or []

        for posisi, item in enumerate(entries, start=1):

            if item and item.get("id") == target_video_id:

                return {
                    "posisi": posisi,
                    "judul": item.get("title", "") or "",
                    "link": (
                        "https://www.youtube.com/watch?v="
                        + target_video_id
                    )
                }

        return None

    except Exception as e:

        print("\nGagal membaca hasil:")
        print(e)

        return None


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 65)
    print("             YOUTUBE KEYWORD BY ObodSC")
    print("=" * 65)

    link = input(
        "\nMasukkan link video YouTube: "
    ).strip()

    video_id = ambil_video_id(link)

    if not video_id:
        print("\nLink YouTube tidak valid.")
        return

    print("\nVideo ID:", video_id)

    # ========================================================
    # INFORMASI VIDEO
    # ========================================================

    info = ambil_info_video(video_id)

    if not info:
        return

    print("\n" + "=" * 65)
    print("INFORMASI VIDEO")
    print("=" * 65)

    print("Judul   :", info["judul"])
    print("Channel :", info["channel"])
    print("Video ID:", info["id"])

    # ========================================================
    # BUAT KEYWORD
    # ========================================================

    keywords = buat_keyword(info["judul"], info["channel"])

    if not keywords:
        print("\nTidak berhasil membuat keyword.")
        return

    print("\n" + "=" * 65)
    print("KEYWORD YANG AKAN DIUJI")
    print("=" * 65)

    for i, keyword in enumerate(keywords, start=1):
        print(f"{i}. {keyword}")

    # ========================================================
    # TEST SEMUA KEYWORD
    # ========================================================

    hasil = []

    print("\n" + "=" * 65)
    print("MEMULAI PENGUJIAN OTOMATIS")
    print("=" * 65)

    for nomor, keyword in enumerate(keywords, start=1):

        print("\n" + "-" * 65)
        print(f"[{nomor}/{len(keywords)}]")
        print("Keyword:", keyword)
        print("Sedang mencari...")

        data = cari_posisi(keyword, video_id)

        if data:

            print("Video ditemukan:", f"#{data['posisi']}")

            hasil.append({
                "keyword": keyword,
                "posisi": data["posisi"],
                "link": data["link"]
            })

        else:

            print(
                "Video tidak ditemukan "
                f"dalam {JUMLAH_HASIL} hasil pertama."
            )

            hasil.append({
                "keyword": keyword,
                "posisi": None,
                "link": None
            })

        # Jeda antar pencarian
        time.sleep(1.5)

    # ========================================================
    # HASIL AKHIR
    # ========================================================

    ditemukan = [x for x in hasil if x["posisi"] is not None]
    ditemukan.sort(key=lambda x: x["posisi"])

    print("\n\n")
    print("=" * 65)
    print("                 HASIL AKHIR")
    print("=" * 65)

    if not ditemukan:

        print(
            "\nVideo tidak ditemukan "
            "dalam keyword yang diuji."
        )

    else:

        for i, data in enumerate(ditemukan, start=1):
            print(f"{i}. #{data['posisi']}  {data['keyword']}")

        terbaik = ditemukan[0]

        print("\n" + "=" * 65)
        print("                 HASIL TERATAS")
        print("=" * 65)

        print("\nKeyword :", terbaik["keyword"])
        print("Posisi  :", f"#{terbaik['posisi']}")
        print("Video   :", terbaik["link"])

    print()
    input("Tekan ENTER untuk keluar...")


if __name__ == "__main__":
    main()
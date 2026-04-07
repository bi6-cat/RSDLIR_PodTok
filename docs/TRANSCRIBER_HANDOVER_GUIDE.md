# Handover Guide - Transcript Pipeline

## 1. Muc tieu tai lieu
Tai lieu nay dung de ban giao cho nguoi tiep theo:
- Cach chay pipeline transcript tu audio da cat.
- Giai thich cau truc input/output.
- Mo ta cac thay doi da lam gan day (bo sung % tien do).
- Cac luu y khi van hanh va debug.

## 2. Tong quan luong xu ly
Script chinh: `src/data_processing/transcriber.py`

Pipeline:
1. Quet cac file audio trong `data/*_split/**` theo dinh dang: `.mp3`, `.m4a`, `.wav`.
2. Voi moi file audio:
- Neu da ton tai transcript `.json` tuong ung trong `data/transcripts/...` thi bo qua.
- Neu chua co transcript thi goi Faster-Whisper de nhan dien tieng noi (language="vi").
3. Luu ket qua JSON gom:
- `full_text`: toan bo transcript da ghep.
- `segments`: danh sach doan co `start`, `end`, `text`.

## 3. Cau truc thu muc
Input:
- Audio da cat nam trong cac thu muc co hau to `_split` ben duoi `data/`.

Output:
- Transcript JSON luu trong `data/transcripts/`.
- Script giu nguyen cau truc tuong doi cua thu muc input.

Vi du:
- Input: `data/raw_audio_1_split/apple_abc_split.m4a`
- Output: `data/transcripts/raw_audio_1_split/apple_abc_split.json`

## 4. Cach chay
Tai root du an:

```bash
python src/data_processing/transcriber.py
```

Neu may co GPU CUDA:
- Script uu tien `device="cuda"`, `compute_type="float16"`.

Neu CUDA loi/khong co GPU:
- Script tu dong fallback sang CPU voi `compute_type="int8"`.

## 5. Log tien do (da bo sung)
### 5.1. Tien do tong theo file
Moi file audio se in 1 dong tien do tong:

```text
📁 Tiến độ tổng transcript: 12/120 (10%) - apple_xxx_split.m4a
```

Y nghia:
- `12/120`: file thu 12 trong tong 120 file audio tim thay.
- `(10%)`: phan tram tien do toan bo danh sach quet.

### 5.2. Tien do chi tiet theo segment trong 1 file
Khi dang transcribe 1 file, script in tien do theo segment:

```text
🎙️ Đang bóc băng... (0/245 - 0%)
   ↳ Tiến độ segment: 13/245 (5%)
   ↳ Tiến độ segment: 25/245 (10%)
   ...
   ↳ Tiến độ segment: 245/245 (100%)
✅ Bóc băng xong!
```

Y nghia:
- Tong so segment duoc tinh truoc bang cach ep generator ve list.
- Log duoc gioi han moi moc 5% de tranh nhiu terminal.

### 5.3. Tong ket cuoi chuong trinh
Sau khi quet xong danh sach:

```text
🎯 Hoàn tất vòng lặp transcript. File mới được tạo: X/Y
```

- `X`: so file transcript moi tao trong lan chay nay.
- `Y`: tong so file audio duoc quet.

## 6. Nhung gi da lam (cap nhat 2026-04-07)
Da cap nhat trong `src/data_processing/transcriber.py`:
- Them `% tien do tong` cho tung file audio khi chay batch.
- Them `% tien do segment` cho tung file dang transcribe.
- Them tong ket so luong file transcript moi tao sau khi chay xong.
- Giu nguyen hanh vi cu:
- Van bo qua file da co transcript.
- Van fallback CPU neu CUDA gap loi.
- Van luu JSON theo dung cau truc thu muc con.

## 7. Luu y van hanh
- Lan dau chay tren CPU co the rat cham voi model `medium`.
- Neu muon nhanh hon co the giam model size (`small`), doi lai do chinh xac co the giam.
- Truong hop audio hong/khong doc duoc:
- Script in loi va bo qua file do, khong dung ca batch.

## 8. Checklist cho nguoi tiep theo
1. Kiem tra da co audio trong cac thu muc `data/*_split/`.
2. Chay script transcript.
3. Theo doi log `% tien do tong` va `% segment`.
4. Kiem tra file JSON duoc tao dung vi tri du kien trong `data/transcripts/`.
5. Neu can benchmark toc do, ghi lai:
- So file moi tao duoc.
- Tong thoi gian chay.
- GPU/CPU va model size da dung.

## 9. Goi y cai tien tiep
- Them mode resume thong minh theo danh sach pending de khong can quet lai toan bo.
- Ghi log ra file (VD: `logs/transcriber.log`) de de theo doi batch lon.
- Them tham so CLI cho `model_size` va `language`.

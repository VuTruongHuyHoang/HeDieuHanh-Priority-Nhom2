def chay_thuattoan_fcfs(danh_sach_tien_trinh):
    ds_fcfs = sorted(list(danh_sach_tien_trinh), key=lambda x: x["AT"])
    thoi_gian_hien_tai = 0
    tong_wt = 0
    tong_tat = 0
    ket_qua = []
    for p in ds_fcfs:
        if thoi_gian_hien_tai < p["AT"]:
            thoi_gian_hien_tai = p["AT"]
        thoi_gian_hoan_thanh = thoi_gian_hien_tai + p["BT"]
        tat = thoi_gian_hoan_thanh - p["AT"]
        wt = tat - p["BT"]
        thoi_gian_hien_tai = thoi_gian_hoan_thanh
        tong_tat += tat
        tong_wt += wt
        ket_qua.append({
            "PID": p["PID"],
            "AT": p["AT"],
            "BT": p["BT"],
            "PR": p["PR"],
            "TAT": tat,
            "WT": wt
        })
    so_luong = len(ds_fcfs)
    wt_trung_binh = round(tong_wt / so_luong, 2) if so_luong > 0 else 0
    tat_trung_binh = round(tong_tat / so_luong, 2) if so_luong > 0 else 0
    return ket_qua, wt_trung_binh, tat_trung_binh
if __name__ == "__main__":
    import dummy_data
    print("=== CHẠY THỬ THUẬT TOÁN FCFS (MODULE 7) ===")
    kq, wt_tb, tat_tb = chay_thuattoan_fcfs(dummy_data.danh_sach_test)
    print(f"{'PID':<5} | {'AT':<5} | {'BT':<5} | {'TAT':<5} | {'WT':<5}")
    print("-" * 35)
    for p in kq:
        print(f"{p['PID']:<5} | {p['AT']:<5} | {p['BT']:<5} | {p['TAT']:<5} | {p['WT']:<5}")
    print("-" * 35)
    print(f"Thời gian chờ trung bình (Avg WT)    : {wt_tb}")
    print(f"Thời gian lưu lại trung bình (Avg TAT): {tat_tb}")

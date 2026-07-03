#!/usr/bin/env python3
import sys
import random
import re

# ---------------------------- Các hàm tiện ích ----------------------------
def random_string(length=8):
    return ''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ', k=length))

def random_int(a=1, b=100):
    return random.randint(a, b)

# Tạo một đoạn mã giả (hàm, biến, vòng lặp vô nghĩa)
def gen_dummy_block(depth=0):
    lines = []
    # 1. Tạo một vài biến địa phương
    for _ in range(random_int(2, 5)):
        v = random_string()
        lines.append(f"local {v} = {random_int(1, 99)} + {random_int(1, 99)}")
    # 2. Tạo một hàm giả (không gọi, hoặc gọi sau)
    func_name = random_string()
    lines.append(f"local function {func_name}({random_string()})")
    lines.append(f"    local {random_string()} = {random_int(10, 50)}")
    lines.append(f"    for {random_string()}=1,{random_int(3,7)} do")
    lines.append(f"        {random_string()} = {random_string()} + {random_int(1,5)}")
    lines.append(f"    end")
    lines.append(f"    return {random_string()} or {random_int(0,1)}")
    lines.append(f"end")
    # 3. Gọi hàm giả một cách vô ích (nếu muốn)
    if random.random() > 0.5:
        lines.append(f"local {random_string()} = {func_name}({random_int(0,9)})")
    # 4. Thêm một vòng lặp for rỗng hoặc với biến không dùng
    for _ in range(random_int(1, 3)):
        lines.append(f"for {random_string()}=1,{random_int(5,15)} do end")
    return '\n'.join(lines)

# Chèn các đoạn giả vào các vị trí ngẫu nhiên trong script
def insert_dummy_blocks(code, num_blocks=4):
    lines = code.split('\n')
    if len(lines) < 10:
        # Nếu script ngắn, chèn trực tiếp vào cuối
        dummy = gen_dummy_block()
        return code + '\n' + dummy + '\n'
    # Chèn ở các vị trí khác nhau
    for _ in range(num_blocks):
        idx = random.randint(1, len(lines) - 1)
        dummy = gen_dummy_block()
        lines.insert(idx, dummy)
    return '\n'.join(lines)

# Làm rối luồng điều khiển (thêm if rác, thay đổi điều kiện)
def control_flow_obfuscation(code):
    # 1. Tìm các khối if ... then (đơn giản) và thêm điều kiện giả
    #    Sử dụng regex để tìm các if ... then, nhưng không lồng nhau
    #    Ta sẽ thay một vài if đơn giản thành dạng phức tạp hơn
    #    Ví dụ: if a == b then -> if (a == b) and (1 == 1) then
    #    Nhưng điều này có thể phá vỡ cú pháp nếu có dấu ngoặc, ta làm cẩn thận.
    #    Thay vì sửa, ta chèn thêm các if-else rác không bao giờ đúng.
    
    lines = code.split('\n')
    new_lines = []
    for line in lines:
        # Tìm dòng bắt đầu bằng "if " và kết thúc bằng " then"
        if re.match(r'^\s*if\s+', line) and ' then' in line:
            # Thêm một điều kiện luôn đúng: (phần_điều_kiện) or false
            # Lấy phần điều kiện
            stripped = line.strip()
            # Tìm vị trí của " then"
            then_pos = stripped.find(' then')
            if then_pos != -1:
                condition = stripped[3:then_pos].strip()  # bỏ "if" và "then"
                # Tạo biến giả
                dummy_var = random_string()
                # Thêm điều kiện phức tạp: (condition) and (dummy_var == dummy_var)
                new_condition = f"({condition}) and ({dummy_var} == {dummy_var})"
                new_line = f"if {new_condition} then"
                # Chèn thêm khai báo biến giả trước if (nhưng chỉ thêm ở đầu dòng)
                # Ta sẽ chèn biến dummy ở dòng trước
                new_lines.append(f"local {dummy_var} = {random_int(1,100)}")
                new_lines.append(new_line)
                continue
        new_lines.append(line)
    code = '\n'.join(new_lines)
    
    # 2. Chèn thêm các khối if-else rác (không bao giờ đúng) ở cuối một số khối
    #    Tìm các dòng "end" và chèn trước đó một if false
    #    Cách này có thể gây lỗi, ta thực hiện đơn giản: chèn vào cuối file
    dummy_if = """
-- Dummy control flow
if 1 == 2 then
    local a = 0
    for i = 1, 10 do a = a + i end
else
    local b = 0
    for i = 1, 10 do b = b - i end
end
"""
    code = code + '\n' + dummy_if
    
    # 3. Chèn các vòng lặp for giả vào các vị trí ngẫu nhiên (không ảnh hưởng)
    lines = code.split('\n')
    for _ in range(3):
        idx = random.randint(1, len(lines)-1)
        dummy_loop = f"for {random_string()}=1,{random_int(3,7)} do local {random_string()}={random_int(0,9)} end"
        lines.insert(idx, dummy_loop)
    code = '\n'.join(lines)
    
    return code

# ---------------------- Hàm obfuscate chính (nâng cấp) ----------------------
def obfuscate_lua(code):
    # Bước 1: Chèn các khối dummy function và biến giả
    code = insert_dummy_blocks(code, num_blocks=5)
    
    # Bước 2: Làm rối luồng điều khiển
    code = control_flow_obfuscation(code)
    
    # Bước 3: Mã hóa đa lớp (5 lớp XOR + đảo ngược)
    keys = [random.randint(1, 255) for _ in range(5)]
    data = code.encode('utf-8')
    for i, k in enumerate(keys):
        if i % 2 == 0:
            data = bytes([b ^ k for b in data])
        else:
            data = bytes([b ^ k for b in data[::-1]])
    hex_data = data.hex()
    
    # Bước 4: Tạo loader với giải mã ngược
    loader_lines = []
    loader_lines.append("-- Obfuscated by MoonSec & We Are Dev (Pro+)")
    loader_lines.append("local function d1(s,k)")
    loader_lines.append("  local t={}")
    loader_lines.append("  for i=1,#s do")
    loader_lines.append("    t[i]=string.char((s:byte(i)~k))")
    loader_lines.append("  end")
    loader_lines.append("  return table.concat(t)")
    loader_lines.append("end")
    loader_lines.append("local function d2(s,k)")
    loader_lines.append("  local t={}")
    loader_lines.append("  for i=#s,1,-1 do")
    loader_lines.append("    t[#t+1]=string.char((s:byte(i)~k))")
    loader_lines.append("  end")
    loader_lines.append("  return table.concat(t)")
    loader_lines.append("end")
    loader_lines.append("local function h2b(s)")
    loader_lines.append("  local t={}")
    loader_lines.append("  for i=1,#s,2 do")
    loader_lines.append("    t[#t+1]=string.char(tonumber(s:sub(i,i+1),16))")
    loader_lines.append("  end")
    loader_lines.append("  return table.concat(t)")
    loader_lines.append("end")
    loader_lines.append(f"local data = h2b('{hex_data}')")
    loader_lines.append(f"data = d1(data, {keys[4]})")
    loader_lines.append(f"data = d2(data, {keys[3]})")
    loader_lines.append(f"data = d1(data, {keys[2]})")
    loader_lines.append(f"data = d2(data, {keys[1]})")
    loader_lines.append(f"data = d1(data, {keys[0]})")
    loader_lines.append("loadstring(data)()")
    loader = '\n'.join(loader_lines)
    
    # Bước 5: Thêm dead code và kiểm tra môi trường
    final = gen_dummy_block() + '\n'
    final += "if not game then return end\nif not workspace then return end\n"
    final += loader
    return final

# ------------------------------ Main ---------------------------------------
def main():
    if len(sys.argv) < 2:
        print("Usage: python lua_obfuscator_pro_plus.py <input.lua> [output.lua]")
        sys.exit(1)
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else input_file + ".obf.lua"
    
    with open(input_file, 'r', encoding='utf-8') as f:
        code = f.read()
    
    obf = obfuscate_lua(code)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(obf)
    
    print(f"✅ Pro+ obfuscation completed. Output: {output_file}")

if __name__ == "__main__":
    main()

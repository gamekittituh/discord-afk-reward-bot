# discord-afk-reward-bot

Bot สำหรับ Discord ที่ช่วยจัดการสถานะ AFK (Away From Keyboard) และแจกของรางวัลหรือแต้มให้กับสมาชิกที่ใช้งานระบบ AFK ในเซิร์ฟเวอร์

## ฟีเจอร์หลัก

- ตั้งสถานะ AFK พร้อมข้อความส่วนตัว
- แจ้งเตือนเมื่อมีคน mention ผู้ที่ AFK
- แจกแต้ม/รางวัลเมื่อกลับจากโหมด AFK (Reward System)
- ตรวจสอบแต้ม/ของรางวัลของตัวเอง
- เก็บสถิติการใช้งาน AFK

## การติดตั้ง

1. **โคลนโปรเจค**
    ```bash
    git clone https://github.com/gamekittituh/discord-afk-reward-bot.git
    cd discord-afk-reward-bot
    ```

2. **ติดตั้ง dependencies**  
   หากใช้ Node.js (discord.js)
    ```bash
    npm install
    ```
   หากใช้ Python (discord.py)
    ```bash
    pip install -r requirements.txt
    ```

3. **ตั้งค่า Environment Variables**
    - สร้างไฟล์ `.env`
    - ใส่ TOKEN และคีย์สำคัญต่าง ๆ เช่น
      ```
      DISCORD_TOKEN=your_discord_bot_token
      ```

4. **รันบอท**
    - Node.js:
      ```bash
      node index.js
      ```
    - Python:
      ```bash
      python bot.py
      ```

## วิธีใช้งาน

- `!afk [ข้อความ]`  
  ตั้งสถานะ AFK พร้อมข้อความ
- เมื่อมีสมาชิก mention ผู้ที่ AFK  
  บอทจะแจ้งเตือนอัตโนมัติ
- เมื่อพิมพ์ข้อความหลังจาก AFK  
  บอทจะลบสถานะ AFK และแจกแต้ม/รางวัล
- `!rewards`  
  ตรวจสอบแต้ม/ของรางวัลของตัวเอง

## การตั้งค่าระบบรางวัล

คุณสามารถปรับแต้ม/ของรางวัลได้ในไฟล์ config หรือผ่านคำสั่ง (ขึ้นอยู่กับการพัฒนา)

## License

Distributed under the MIT License. See `LICENSE` for more information.

## ติดต่อ

- [GitHub Issues](https://github.com/gamekittituh/discord-afk-reward-bot/issues)
- ผู้พัฒนา: [gamekittituh](https://github.com/gamekittituh)

---

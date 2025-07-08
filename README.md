# discord-afk-reward-bot

Bot สำหรับ Discord ที่ช่วยจัดการสถานะ AFK (Away From Keyboard) และแจกของรางวัลหรือแต้มให้กับสมาชิกที่ใช้งานระบบ AFK ในเซิร์ฟเวอร์

## ฟีเจอร์หลัก

- ตั้งสถานะ AFK พร้อมข้อความส่วนตัว
- แจ้งเตือนเมื่อมีคน mention ผู้ที่ AFK
- แจก EXP เมื่อกลับจากโหมด AFK ตามระยะเวลา
- ระบบแรงค์ (Ranking) ตาม EXP ที่สะสม
- ตรวจสอบ EXP และแรงค์ของตัวเอง
- Leaderboard อันดับ EXP สูงสุด
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
    - สร้างไฟล์ `.env` (สามารถคัดลอกจาก `.env.example`)
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
  ตั้งสถานะ AFK พร้อมข้อความ (ไม่บังคับ)
- เมื่อมีสมาชิก mention ผู้ที่ AFK  
  บอทจะแจ้งเตือนอัตโนมัติ
- เมื่อพิมพ์ข้อความหลังจาก AFK  
  บอทจะลบสถานะ AFK และแจก EXP ตามระยะเวลา
- `!exp` หรือ `!rank`  
  ตรวจสอบ EXP และแรงค์ของตัวเอง
- `!top` หรือ `!leaderboard`  
  ดู Leaderboard อันดับ EXP สูงสุด

## การตั้งค่าระบบรางวัล

คุณสามารถปรับแต่งระบบ EXP และแรงค์ได้ในไฟล์ config:

- **rank_config.json**: กำหนดช่วง EXP และชื่อแรงค์
- **afk.json**: ข้อมูลผู้ใช้ (จะถูกสร้างอัตโนมัติ)
- **exp_per_minute**: กำหนดจำนวน EXP ต่อนาที AFK ใน rank_config.json

## License

Distributed under the MIT License. See `LICENSE` for more information.

## ติดต่อ

- [GitHub Issues](https://github.com/gamekittituh/discord-afk-reward-bot/issues)
- ผู้พัฒนา: [gamekittituh](https://github.com/gamekittituh)

---

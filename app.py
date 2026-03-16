<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>เกมปราบผี 👻</title>
    <style>
        body {
            background-color: #1a1a2e; /* พื้นหลังสีมืดๆ ดูลึกลับ */
            color: white;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            text-align: center;
            margin: 0;
            overflow: hidden; 
        }
        #game-board {
            width: 100vw;
            height: 80vh;
            position: relative;
            background-color: #16213e;
            cursor: crosshair; /* เปลี่ยนเมาส์เป็นเป้าเล็ง */
            border-top: 3px solid #e94560;
        }
        #ghost {
            font-size: 60px; /* ขนาดตัวผี */
            position: absolute;
            top: 50%;
            left: 50%;
            cursor: pointer;
            user-select: none;
            transition: top 0.2s, left 0.2s; /* ให้ผีลอยสมูทขึ้น */
        }
        h1 { margin-top: 20px; color: #e9

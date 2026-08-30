<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Tilting Icons</title>
    <style>
        body {
            background-color: #FAF7F2;
            font-family: 'Inter', -apple-system, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
        }

        .container {
            display: flex;
            gap: 40px;
        }

        .category-card {
            background-color: #FFFFFF;
            border: 1px solid #E8E0D5;
            padding: 30px 20px;
            border-radius: 16px;
            text-align: center;
            cursor: pointer;
            box-shadow: 0 4px 12px rgba(46, 39, 36, 0.03);
            width: 120px;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }

        .category-card:hover {
            box-shadow: 0 6px 16px rgba(46, 39, 36, 0.08);
        }

        .icon {
            font-size: 3rem;
            display: inline-block;
            transition: transform 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        }

        .category-text {
            margin-top: 15px;
            font-size: 1rem;
            font-weight: 700;
            color: #1A1614; /* High-contrast black font */
        }
    </style>
</head>
<body>

    <div class="container">
        <!-- Category 1 -->
        <div class="category-card" onclick="alert('Clicked Category One!')">
            <div class="icon">🏠</div>
            <div class="category-text">Category 1</div>
        </div>

        <!-- Category 2 -->
        <div class="category-card" onclick="alert('Clicked Category Two!')">
            <div class="icon">📊</div>
            <div class="category-text">Category 2</div>
        </div>

        <!-- Category 3 -->
        <div class="category-card" onclick="alert('Clicked Category Three!')">
            <div class="icon">💡</div>
            <div class="category-text">Category 3</div>
        </div>
    </div>

    <script>
        // Add dynamic tilting effect on mouse movement over each card
        const cards = document.querySelectorAll('.category-card');

        cards.forEach(card => {
            const icon = card.querySelector('.icon');

            card.addEventListener('mousemove', (e) => {
                const rect = card.getBoundingClientRect();
                const x = e.clientX - rect.left; // Mouse X inside card
                const centerX = rect.width / 2;
                
                // Calculate tilt angle based on mouse position
                const tiltAngle = ((x - centerX) / centerX) * 15; 
                icon.style.transform = `rotate(${tiltAngle}deg) scale(1.1)`;
            });

            card.addEventListener('mouseleave', () => {
                icon.style.transform = 'rotate(0deg) scale(1)';
            });
        });
    </script>

</body>
</html>

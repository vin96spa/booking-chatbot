/** @type {import('tailwindcss').Config} */

import tailwindScrollbar from 'tailwind-scrollbar';

export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    darkMode: 'selector',
    theme: {
        extend: {
            screens: {
                'xxl': '1440px', // added for big screens
            },
            fontFamily: {
                sans: ['Inter', 'sans-serif'],
            },
            backgroundImage: {
                'custom-bg': "url('@/assets/images/background.jpg')",
            },
            keyframes: {

            },
            animation: {
            },
            
        },
    },
    plugins: [tailwindScrollbar],
}


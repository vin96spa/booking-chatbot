/** @type {import('tailwindcss').Config} */

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
                'custom-bg': "bg-[linear-gradient(to_bottom,#62405A,#7B3F6D,#AC3557,#4E74A8,#9B658E)]",
            },
            keyframes: {

            },
            animation: {
            },
            
        },
    },
    plugins: [],
}


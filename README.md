VEX TUNER // FORZA EDITION



An advanced, AI-powered vehicle dynamics and suspension tuning generator designed specifically for racing simulators and arcade racers. Built for FFB wheels but can be used for other devices, it computes precision setup matrices based on your vehicle, performance class, drivetrain layout, and control input hardware.



FEATURES



- Precision AI Calculations: Uses structured JSON schemas to ensure reliable, mathematically sound vehicle configurations.

- Hardware-Tailored Profiles: Optimizes feedback curves and handling characteristics depending on whether you use a standard controller, a Direct Drive wheel base (Fanatec, Moza, Simucube, Logitech, etc.), or a desktop setup.

- Interactive Adjustments: Test your tune, input handling complaints (e.g., “understeering on entry”), and let the AI instantly recalculate and fix the specific parameters.

- Save & Load Support: Easily save your custom tunes as .json files and load them back into the app whenever you need them.



INSTRUCTIONS



1. Requirements & Setup

- You will need a valid Gemini API key to power the tuning engine. You can enter it directly into the application interface.

- Download the compiled .exe from the GitHub Releases https://github.com/Vexsys13/Vex-Tuner-FH6/releases/tag/V2.0

-Make your own API key to use by going to https://aistudio.google.com/app/api-keys

***⚠️!!! Important Security Note: Never publish, share, or commit your API keys to public repositories or front-end code !!!⚠️***

2. How to Use

- Enter Credentials: Type or paste your Gemini API key into the License/Engine API key field on the left panel or ctrl+V to paste.

- Select Vehicle: Choose a car brand and model from the dropdown menus, or select Other / Custom to type your own vehicle name.

- Configure Specs: 

  * Input the car's weight in lbs (or leave the default estimate).

  * Select your target Performance Index (PI) class (S1, A, X, etc.).

  * Choose your drivetrain layout (AWD, RWD, FWD).

  * Select your hardware device (Controller or specific Wheel Base) so the AI can tailor the steering response.

  * Pick your handling style (Sim Racing, Road Race, Drift, etc.).

- Build Tune: Click BUILD TUNE and wait a moment for the matrix to compute. Your detailed, formatted tune sheet will appear on the right.

- Fine-Tune (Optional): If the car feels loose or pushes in corners, type your handling feedback into the Adjust Setup box at the bottom right and click ADJUST TUNE.

- Save: Click SAVE TUNE to back up your configuration to a .json file on your computer.



LICENSE & USAGE



Copyright (c) 2026 Vexsys13. All Rights Reserved.



- Permissions: You may view the source code for learning purposes and download/run the compiled software for personal, non-commercial use.

- Restrictions: You are strictly prohibited from re-uploading, redistributing, or hosting this code or any compiled binaries (.exe files) on any other platform. 


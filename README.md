# Bovine Care

A comprehensive web application designed to assist cattle farmers by detecting bovine diseases such as Lumpy Skin Disease and Ringworm, while also providing communication tools between farmers and veterinary doctors.

##  Features

* **Disease Detection:**
  Upload images or videos of cattle to detect diseases using AI models (YOLO & MobileNet).

* **Farmer Dashboard:**

  * Image/Video upload section for disease detection.
  * Chatbox for community discussions among farmers.

* **Doctor Dashboard:**

  * Respond to farmer queries.
  * Monitor disease detection requests.

* **Authentication:**
  Login & registration for farmers and doctors via Firebase.

---

##  Tech Stack

* **Frontend:** HTML, CSS, JavaScript
* **Backend:** Python (Flask)
* **Machine Learning Models:** YOLO, MobileNet
* **Database & Auth:** Firebase

---

##  Installation & Setup

1. **Clone the repository:**

```bash
git clone https://github.com/Aswin-MS/Bovine-Care.git
cd Bovine-Care
```

2. **Install dependencies:**

```bash
pip install -r requirements.txt
```

3. **Run the Flask server:**

```bash
python app.py
```

4. **Open the app in your browser:**

```
http://127.0.0.1:5000/
```

---

## 📂 Project Structure

```
Bovine-Care/
│
├── app.py                    # Flask backend server
├── templates/                # HTML files
├── assets/                   # CSS, JS, Images (Note: certain JS files for Firebase config are missing)
├── backend/                  # ML Models & detection scripts
├── static/                   # Processed output files
├── chatbox/                  # Community chatbox feature
├── requirements.txt          # Python dependencies
└── README.md                 # Project documentation
```

---

## ⚠️ Important Notes

* ⚠️ **Missing Files Alert:**
  The following frontend files are not present in this repository due to security cleanup:

  * `assets/js/doctorlogin.js`
  * `assets/js/farmerregister.js`
  * * `assets/js/farmerlogin.js`

  These files contained sensitive Firebase API keys.
  You must **recreate these files manually** or configure Firebase securely (preferably via environment variables) for full authentication functionality.

* The `backend/LumpyDisease.keras` model exceeds GitHub's 50MB limit. Use Git LFS if needed.

* Firebase configuration files are essential for authentication and database operations.

---

## 🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.

---

## 📧 Contact

Aswin M S
GitHub: [Aswin-MS](https://github.com/Aswin-MS)

---

## 📝 License

This project is licensed under the MIT License.

# 🎯 SIMPLE REAL VOTER SETUP

## 📋 **What You Need**

1. **Your real voter ID number**
2. **Your face photo** (clear selfie - save as JPG)
3. **Your eye/iris photo** (close-up of eye - save as JPG)
4. **Your friends' data** (same format)

## 🔧 **Setup Steps**

### 1. **Clear Old Data**
```bash
cd /Users/siddhantmanglam/Documents/vote_auth
source venv_full/bin/activate
python backend/add_real_voters.py
# Choose option 3 to clear all demo data
```

### 2. **Add Your Real Data**

**For each person (you + 4 friends):**

1. **Prepare images** in this folder:
   ```
   backend/real_voter_data/images/
   ```

2. **Name your images**:
   - `ABC1234567_face.jpg` (your voter ID + _face.jpg)
   - `ABC1234567_iris.jpg` (your voter ID + _iris.jpg)

3. **Run the script**:
   ```bash
   python backend/add_real_voters.py
   # Choose option 1 to add voter
   # Enter your details when prompted
   ```

4. **Repeat for all 5 people**

### 3. **Image Requirements**

**Face Photo:**
- Clear front-facing photo
- Good lighting
- No glasses (if possible)
- JPG format

**Iris Photo:**
- Close-up of eye
- Clear iris pattern visible
- Good lighting, no flash
- JPG format

### 4. **Example Data Entry**

```
Voter ID: ABC1234567
Name: Your Name
Age: 25
Address: Your Address
Phone: 9876543210
Booth: 001
```

## 🚀 **Demo Flow**

1. **Start system**:
   ```bash
   # Terminal 1
   python backend/app.py
   
   # Terminal 2
   cd frontend && npm start
   ```

2. **Go to**: http://localhost:3000

3. **Demo steps**:
   - Click "Voter Verification"
   - Select booth
   - Enter YOUR real voter ID
   - Complete face verification (webcam)
   - Complete iris verification (webcam)
   - Vote recorded!

## 🎯 **SIH Presentation**

**"I'll demonstrate our system using real voter data..."**

1. Show your actual voter ID entry
2. Live face recognition with your face
3. Live iris detection with your eye
4. Real-time fraud prevention
5. Blockchain vote recording
6. Dashboard statistics

**Much more impressive than fake demo data! 🏆**

## 📂 **File Structure**

```
backend/real_voter_data/images/
├── ABC1234567_face.jpg    (Your face)
├── ABC1234567_iris.jpg    (Your iris)
├── DEF7890123_face.jpg    (Friend 1)
├── DEF7890123_iris.jpg    (Friend 1 iris)
└── ... (more friends)
```

**Simple, clean, and ready for professional demo! ✨**

import os
import pickle
import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score
from sklearn.metrics import confusion_matrix
import seaborn as sns
import sqlite3

# Database connection
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "..", "database", "college_system.db")


def authenticate(username, password):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT role FROM users
        WHERE username=? AND password=?
    """, (username, password))

    result = cursor.fetchone()
    conn.close()

    return result[0] if result else None


st.title("🎓 Engineering College Academic AI System")

if "role" not in st.session_state:
    st.session_state.role = None


if st.session_state.role is None:

    st.subheader("Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        role = authenticate(username, password)

        if role:
            st.session_state.role = role
            st.success(f"Logged in as {role}")
            st.rerun()
        else:
            st.error("Invalid credentials")


if st.session_state.role == "admin":

    st.header("👨‍💼 Admin Panel")

    menu = st.sidebar.selectbox(
        "Admin Menu",
        ["Create Student", "Create Teacher", "View Students"]
    )

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    if menu == "Create Student":

        st.subheader("Create New Student")

        name = st.text_input("Student Name")
        department = st.selectbox("Department", ["CSE", "CIVIL"])
        admission_year = st.number_input("Admission Year", 2020, 2030, 2023)
        semester = st.number_input("Current Semester", 1, 8, 1)
        password = st.text_input("Password", type="password")

        if st.button("Create Student"):

            # Generate student username like CSE2023_01
            prefix = department[:3].upper()
            cursor.execute("SELECT COUNT(*) FROM users WHERE role='student'")
            count = cursor.fetchone()[0] + 1
            username = f"{prefix}{admission_year}_{count:02d}"

            # Get department id
            cursor.execute("SELECT id FROM departments WHERE name=?", (department,))
            dept_id = cursor.fetchone()[0]

            # Insert into users
            cursor.execute("""
                INSERT INTO users (username, password, role, department_id)
                VALUES (?, ?, 'student', ?)
            """, (username, password, dept_id))

            user_id = cursor.lastrowid

            # Insert into students table
            cursor.execute("""
                INSERT INTO students (user_id, admission_year, current_sem)
                VALUES (?, ?, ?)
            """, (user_id, admission_year, semester))

            conn.commit()

            st.success(f"Student Created Successfully! ID: {username}")


elif st.session_state.role == "teacher":

    st.header("👨‍🏫 Teacher Panel")
    st.write("Teacher dashboard coming next...")


elif st.session_state.role == "student":

    st.header("👨‍🎓 Student Panel")

    current_dir = os.path.dirname(__file__)
    model_path = os.path.join(current_dir, "..", "models", "risk_model.pkl")

    # Load model
    model = pickle.load(open(model_path, "rb"))

    # Load dataset
    data_path = os.path.join(current_dir, "..", "data", "student_data.csv")
    data = pd.read_csv(data_path)

    st.sidebar.markdown("## 📊 Admin Dashboard")

    total_students = len(data)
    risk_counts = data["risk_level"].value_counts()

    st.sidebar.write(f"Total Students: {total_students}")
    st.sidebar.write(f"High Risk: {risk_counts.get('High', 0)}")
    st.sidebar.write(f"Medium Risk: {risk_counts.get('Medium', 0)}")
    st.sidebar.write(f"Low Risk: {risk_counts.get('Low', 0)}")

    fig, ax = plt.subplots()
    ax.pie(
        risk_counts,
        labels=risk_counts.index,
        autopct='%1.1f%%'
    )
    ax.set_title("Risk Distribution")

    st.sidebar.pyplot(fig)

    st.title("🎓 Academic Risk Prediction System")
    st.write("Enter student details below:")

    # User Inputs
    attendance = st.slider("Attendance (%)", 50, 100, 75)
    study_hours = st.slider("Study Hours per Week", 1, 35, 10)
    assignments_avg = st.slider("Assignment Average", 0, 100, 60)
    internal_marks = st.slider("Internal Marks", 0, 100, 60)
    previous_gpa = st.slider("Previous GPA", 4.0, 10.0, 7.0)
    absences = st.slider("Number of Absences", 0, 25, 5)
    participation_score = st.slider("Participation Score", 1, 10, 5)
    internet_usage_hours = st.slider("Internet Usage (hrs/day)", 1, 8, 3)
    sleep_hours = st.slider("Sleep Hours per Day", 4, 9, 7)

    if st.button("Predict Risk Level"):

        input_data = np.array([[attendance, study_hours, assignments_avg,
                                internal_marks, previous_gpa, absences,
                                participation_score, internet_usage_hours,
                                sleep_hours]])

        prediction = model.predict(input_data)

        predicted_label = prediction[0]
        risk_map = {0: "High Risk", 1: "Low Risk", 2: "Medium Risk"}

        st.subheader("Prediction Result:")
        st.success(risk_map[predicted_label])

        if prediction[0] == 0:
            st.error("High Risk ⚠️")
            st.write("- Increase study hours")
            st.write("- Improve attendance")
            st.write("- Focus on internal assessments")

        elif prediction[0] == 1:
            st.success("Low Risk ✅")
            st.write("Student is performing well. Maintain consistency!")

        else:
            st.warning("Medium Risk ⚡")
            st.write("- Improve internal marks")
            st.write("- Increase participation")

        new_data = pd.DataFrame([{
            "attendance": attendance,
            "study_hours": study_hours,
            "assignments_avg": assignments_avg,
            "internal_marks": internal_marks,
            "previous_gpa": previous_gpa,
            "absences": absences,
            "participation_score": participation_score,
            "internet_usage_hours": internet_usage_hours,
            "sleep_hours": sleep_hours,
            "risk_level": risk_map[prediction[0]].replace(" Risk", "")
        }])

        existing_data = pd.read_csv(data_path)
        updated_data = pd.concat([existing_data, new_data], ignore_index=True)
        updated_data.to_csv(data_path, index=False)

        if len(updated_data) % 20 == 0:

            st.info("Retraining model with updated dataset...")

            le = LabelEncoder()
            updated_data["risk_encoded"] = le.fit_transform(updated_data["risk_level"])

            X = updated_data.drop(["risk_level", "risk_encoded"], axis=1)
            y = updated_data["risk_encoded"]

            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )

            new_model = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                random_state=42
            )

            new_model.fit(X_train, y_train)

            with open(model_path, "wb") as f:
                pickle.dump(new_model, f)

            model = new_model

    st.markdown("---")
    st.subheader("🔄 Manual Model Retraining")

    if st.button("Retrain Model Now"):

        updated_data = pd.read_csv(data_path)

        le = LabelEncoder()
        updated_data["risk_encoded"] = le.fit_transform(updated_data["risk_level"])

        X = updated_data.drop(["risk_level", "risk_encoded"], axis=1)
        y = updated_data["risk_encoded"]

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        new_model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )

        new_model.fit(X_train, y_train)

        accuracy = accuracy_score(y_test, new_model.predict(X_test))

        y_pred = new_model.predict(X_test)
        cm = confusion_matrix(y_test, y_pred)

        fig_cm, ax_cm = plt.subplots()
        sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", ax=ax_cm)
        ax_cm.set_xlabel("Predicted")
        ax_cm.set_ylabel("Actual")

        st.pyplot(fig_cm)

        with open(model_path, "wb") as f:
            pickle.dump(new_model, f)

        st.success("Model retrained successfully 🚀")
        st.info(f"New Accuracy: {round(accuracy*100,2)}%")
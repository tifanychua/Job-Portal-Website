import { auth } from "./firebase.js";

import {
    createUserWithEmailAndPassword,
    updateProfile
} from "https://www.gstatic.com/firebasejs/11.10.0/firebase-auth.js";

const form = document.getElementById("registerForm");

form.addEventListener("submit", async (e) => {

    e.preventDefault();

    const name = document.getElementById("name").value.trim();
    const email = document.getElementById("email").value.trim();
    const phone = document.getElementById("phone").value.trim();
    const password = document.getElementById("password").value;
    const confirmPassword = document.getElementById("confirm_password").value;

    if (password !== confirmPassword) {
        alert("Passwords do not match.");
        return;
    }

    try {

        // Create Firebase Authentication user
        const credential = await createUserWithEmailAndPassword(
            auth,
            email,
            password
        );

        // Update Firebase display name
        await updateProfile(credential.user, {
            displayName: name
        });

        // Get Firebase ID Token
        const token = await credential.user.getIdToken();

        // Save profile to Firestore through FastAPI
        const response = await fetch("/firebase-register/job-seeker", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                token,
                name,
                phone
            })
        });

        console.log(response.status);

        const result = await response.json();

        console.log(result);

        if (response.ok) {

            window.location.href = "/login?registered=success&role=job_seeker";

        } else {

            alert(JSON.stringify(result));

        }

    } catch (error) {

        alert(error.message);

    }

});
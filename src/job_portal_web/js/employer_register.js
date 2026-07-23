import { auth } from "./firebase.js";

import {
    createUserWithEmailAndPassword,
    updateProfile
} from "https://www.gstatic.com/firebasejs/11.10.0/firebase-auth.js";

const form = document.getElementById("employerForm");
form.addEventListener("submit", async (e) => {

    e.preventDefault();

    const accountEmail = document.getElementById("accountEmail").value.trim();
    const password = document.getElementById("wizardPassword").value;
    const confirmPassword = document.getElementById("wizardConfirmPassword").value;

    if (password !== confirmPassword) {
        alert("Passwords do not match.");
        return;
    }

    try {

        // Create Firebase Authentication Account
        const credential = await createUserWithEmailAndPassword(
            auth,
            accountEmail,
            password
        );

        await updateProfile(credential.user, {
            displayName: document.getElementById("companyName").value
        });

        const token = await credential.user.getIdToken();

        const employerData = {

            token: token,

            companyName: document.getElementById("companyName").value,

            registrationNumber: document.getElementById("registrationNumber").value,

            businessEmail: document.getElementById("businessEmail").value,

            phone:
                document.getElementById("phoneCode").value +
                " " +
                document.getElementById("phone").value,

            industry: document.getElementById("industry").value,

            companySize: document.getElementById("companySize").value,

            companyWebsite: document.getElementById("companyWebsite").value,

            companyDescription: document.getElementById("companyDescription").value,

            address: document.getElementById("companyAddress").value,

            city: document.getElementById("city").value,

            state: document.getElementById("state").value,

            postalCode: document.getElementById("postalCode").value,

            country: document.getElementById("country").value,

            contactFullName:
                document.getElementById("contactFullName").value,

            contactJobTitle:
                document.getElementById("contactJobTitle").value,

            contactDepartment:
                document.getElementById("contactDepartment").value,

            contactEmail:
                document.getElementById("contactEmail").value,

            contactPhone:
                document.getElementById("contactPhoneCode").value +
                " " +
                document.getElementById("contactPhone").value,

            altPhone:
                document.getElementById("altPhone").value
                    ? document.getElementById("altPhoneCode").value +
                      " " +
                      document.getElementById("altPhone").value
                    : "",

            preferredContactMethod:
                document.querySelector(
                    'input[name="preferredContactMethod"]:checked'
                ).value,

            bestTimeToContact:
                document.getElementById("bestTimeToContact").value,

            correspondenceAddress:
                document.getElementById("correspondenceAddress").value,

        };

        const response = await fetch("/firebase-register/employer", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify(employerData)

        });

        const result = await response.json();

        if (response.ok) {

            window.location.href =
                "/login?registered=success&role=employer";

        } else {

            alert(result.error || "Registration failed.");

        }

    } catch (error) {

        alert(error.message);

    }

});
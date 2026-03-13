
  // ── Chip sync with select ──
  const chips = document.querySelectorAll(".chip");
  const select = document.getElementById("subject");
  chips.forEach((chip) => {
    chip.addEventListener("click", () => {
      chips.forEach((c) => c.classList.remove("active"));
      chip.classList.add("active");
      select.value = chip.dataset.val;
    });
  });
  select.addEventListener("change", () => {
    chips.forEach((c) => {
      c.classList.toggle("active", c.dataset.val === select.value);
    });
  });
  // ── Validation ──
  function validate() {
    let valid = true;
    const firstName = document.getElementById("firstName");
    const email = document.getElementById("email");
    const message = document.getElementById("message");
    [firstName, email, message].forEach((el) =>
      el.classList.remove("error"),
    );
    if (!firstName.value.trim()) {
      firstName.classList.add("error");
      valid = false;
    }
    const emailRx = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRx.test(email.value.trim())) {
      email.classList.add("error");
      valid = false;
    }
    if (!message.value.trim()) {
      message.classList.add("error");
      valid = false;
    }
    return valid;
  }
  // ── Submit ──
  const form = document.getElementById("contactForm");
  const submitBtn = document.getElementById("submitBtn");
  const formBody = document.getElementById("formBody");
  const successOverlay = document.getElementById("successOverlay");
  const btnBack = document.getElementById("btnBack");
  form.addEventListener("submit", (e) => {
    e.preventDefault();
    if (!validate()) return;
    submitBtn.classList.add("loading");
    submitBtn.disabled = true;
    // Simulate async send
    setTimeout(() => {
      submitBtn.classList.remove("loading");
      formBody.classList.add("hide");
      successOverlay.classList.add("show");
    }, 1800);
  });
  // Reset
  btnBack.addEventListener("click", () => {
    form.reset();
    chips.forEach((c, i) => c.classList.toggle("active", i === 0));
    select.value = "General Enquiry";
    submitBtn.disabled = false;
    document
      .querySelectorAll(".error")
      .forEach((el) => el.classList.remove("error"));
    successOverlay.classList.remove("show");
    formBody.classList.remove("hide");
  });
  // Live clear errors on input
  document.querySelectorAll("input, textarea").forEach((el) => {
    el.addEventListener("input", () => el.classList.remove("error"));
  });
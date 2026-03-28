
const usernameInput  = document.getElementById('username');
const classDisplay   = document.getElementById('class-display');
const armDisplay     = document.getElementById('arm-display');
const schoolClassInput = document.getElementById('school_class');
const armInput       = document.getElementById('arm');
const fieldClass     = document.getElementById('field-class');
const fieldArm       = document.getElementById('field-arm');


usernameInput.addEventListener('blur', function () {
  const username = this.value.trim();
  if (!username) return;


  fieldClass.classList.add('loading');
  fieldArm.classList.add('loading');
  fieldClass.classList.remove('populated');
  fieldArm.classList.remove('populated');


  fetch(`/api/student-info/?username=${encodeURIComponent(username)}`)
    .then(res => res.json())
    .then(data => {
      fieldClass.classList.remove('loading');
      fieldArm.classList.remove('loading');
      if (data.success) {
        classDisplay.value   = data.school_class;
        armDisplay.value     = data.arm;
        schoolClassInput.value = data.school_class_id;
        armInput.value       = data.arm_id;
        fieldClass.classList.add('populated');
        fieldArm.classList.add('populated');
      } else {
        classDisplay.value = '';
        armDisplay.value   = '';
      }
    })
    .catch(() => {
      fieldClass.classList.remove('loading');
      fieldArm.classList.remove('loading');
    });
});

document.addEventListener('DOMContentLoaded', function() {
  const form = document.getElementById('login-form');
  const usernameField = document.getElementById('field-username');
  const passwordField = document.getElementById('field-password');
  const usernameInput = document.getElementById('username');
  const passwordInput = document.getElementById('password');
  const togglePassword = document.getElementById('toggle-password');

  // Password toggle functionality
  if (togglePassword) {
    togglePassword.addEventListener('click', function() {
      const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
      passwordInput.setAttribute('type', type);
      
      // Change icon
      const icon = this.querySelector('.eye-icon');
      icon.textContent = type === 'password' ? '👁️' : '🙈';
    });
  }

  // Clear error states when user starts typing
  usernameInput.addEventListener('input', function() {
    usernameField.classList.remove('error');
  });

  passwordInput.addEventListener('input', function() {
    passwordField.classList.remove('error');
  });

  // Form validation on submit
  form.addEventListener('submit', function(e) {
    let isValid = true;

    // Validate username
    if (usernameInput.value.trim() === '') {
      usernameField.classList.add('error');
      isValid = false;
    } else {
      usernameField.classList.remove('error');
    }

    // Validate password
    if (passwordInput.value.trim() === '') {
      passwordField.classList.add('error');
      isValid = false;
    } else {
      passwordField.classList.remove('error');
    }

    // Prevent form submission if invalid
    if (!isValid) {
      e.preventDefault();
    }
  });

  // Add shake animation to error alert if present
  const errorAlert = document.querySelector('.alert-error');
  if (errorAlert) {
    errorAlert.style.animation = 'slideDown 0.3s cubic-bezier(0.22, 0.61, 0.36, 1), shake 0.5s ease 0.3s';
  }
});

// Shake animation for error alert
const style = document.createElement('style');
style.textContent = `
  @keyframes shake {
    0%, 100% { transform: translateX(0); }
    10%, 30%, 50%, 70%, 90% { transform: translateX(-4px); }
    20%, 40%, 60%, 80% { transform: translateX(4px); }
  }
`;
document.head.appendChild(style);

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

function toggleAlarm(action){
  fetch(`/alarm/${action}`);
  alert(`Alarm ${action.toUpperCase()} triggered`);
}

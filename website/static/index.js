function deleteTicket(ticketId) {
  fetch("/delete-ticket", {
    method: "POST",
    body: JSON.stringify({ ticketId: ticketId }),
  }).then((_res) => {
    window.location.href = "/";
  });
}

function deleteUser(userId){
  fetch("/tech/view_users/delete-user", {
    method: 'POST',
    body: JSON.stringify({ userId: userId }),
  }).then((_res) => {
    window.location.href = "/tech/view_users";
  });
}

function signOut(itemId){
  fetch("/tech/equipment_log/sign-out", {
    method: 'POST',
    body: JSON.stringify({ itemId: itemId }),
  }).then((_res) => {
    window.location.href = "/tech/equipment_log";
  });
}

function signIn(itemId){
  fetch("/tech/equipment_log/sign-in", {
    method: 'POST',
    body: JSON.stringify({ itemId: itemId }),
  }).then((_res) => {
    window.location.href = "/tech/equipment_log";
  });
}
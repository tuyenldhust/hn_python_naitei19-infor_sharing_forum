let documento = document.getElementById("documento")
let cep = document.getElementById("cep")
let logradoro = document.getElementById("logradouro")
let numeroCasa = document.getElementById("documento")
let complemento = document.getElementById("complemento")
let numerodomedidor = document.getElementById("numerodomedidor")
let codConsumidor;

//buscar  id pelo cpf

function getConsumidor() {
      fetch(`https://localhost:7230/Consumidor/Documento/${documento.value}`)

  .then(response => response.json())
  .then(data => {
    var apiData = JSON.stringify(data) ;
    codConsumidor = data.cod_Consumidor
  })
  .catch(error => console.error(error));
    };
const newUser = {
    cod_Consumidor :codConsumidor,
    num_medidor : numerodomedidor.value,
    num_casa  : numeroCasa.value,
    cep : cep.value,
    logradouro : logradoro.value,
    Bairro : bairro.value,
    complemento : complemento.value
}

function postUser(newUser) {
    fetch(url, {
      method: "POST",
      body: JSON.stringify(newUser),
      headers: {
        "Content-type": "aplicattion/json",
      },
    })
      .then((response) => response.json())
      .then((data) => (alertApi.textContent = data))
      .catch((error) => console.error(error));
  }

var button = document.getElementById("myButton");
button.addEventListener("Submit", function(e) {
  getConsumidor()
  postUser()
  e.preventDefault()
});

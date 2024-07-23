const canvas = document.getElementById('canvas')
const ctx = canvas.getContext('2d')
let drawing = false

ctx.save()

canvas.addEventListener('mousedown', event => {
  drawing = true
  ctx.moveTo(event.clientX - canvas.offsetLeft, event.clientY - canvas.offsetTop)
})
canvas.addEventListener('mouseup', () => drawing = false)
canvas.addEventListener('mousemove', draw)

function draw(event) {
  if (!drawing) return
  ctx.lineWidth = 10
  ctx.lineCap = 'round'
  ctx.strokeStyle = 'black'

  ctx.lineTo(event.clientX - canvas.offsetLeft, event.clientY - canvas.offsetTop)
  ctx.stroke()
  ctx.beginPath()
  ctx.moveTo(event.clientX - canvas.offsetLeft, event.clientY - canvas.offsetTop)
}

function clearCanvas() {
  ctx.clearRect(0, 0, canvas.width, canvas.height)
}

function submitCanvas() {
  const dataUrl = canvas.toDataURL('image/png')
  fetch('/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ image: dataUrl })
  })
    .then(response => response.json())
    .then(data => {
      document.getElementById('prediction').innerText = `Prediction: ${ data?.prediction }`
      console.log('Prediction:', data?.prediction)
    })
    .catch(error => console.error(error))
}
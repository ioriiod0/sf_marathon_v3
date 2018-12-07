import Game from './Game'
import config from './config'
import axios from 'axios'
import url from 'url'

const parsedUrl = url.parse(window.location.href, true)
const id = parsedUrl.query['id']
const type = parsedUrl.query['type']
const game = new Game('stage', 12, config.manifest)
const clickBtn = document.querySelector('#startBtn')
const input = document.querySelector('#inputId')
const selector = document.querySelector('#replayType')

window.addEventListener('addScore', function(e){
  document.querySelector('#scoreNum').innerHTML = e.detail
})

const loadData = function (type = 'competition', id) {
  const uri = config.rest['data'].replace('${type}', type)
  return axios.get(uri + id)
}

const loadAll = function (type, id) {
  Promise.all([game.preLoad(config.manifest), loadData(type, id)])
    .then(res => {
      const data = res[1].data['replay']
      game.startManual(data)
    })
    .catch()
}

if (id) {
  loadAll(type, id)
}

clickBtn.addEventListener('click', function (e) {
  loadAll(selector.value, input.value)
})

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
  const { score, jobs, value, player } = e.detail
  const scoreDom = document.querySelector(`#scoreNum${player + 1}`)
  const jobsDom = document.querySelector(`#packageNum${player + 1}`)
  const valuesDom = document.querySelector(`#values${player + 1}`)
  scoreDom.innerHTML = score
  jobsDom.innerHTML = jobs
  valuesDom.innerHTML = value
})

const loadData = function (id) {
  const uri = `${config.rest['competition']}/${id}/replay`
  return axios.get(uri)
}

const loadAll = function (id) {
  Promise.all([game.preLoad(config.manifest), loadData(id)])
    .then(res => {
      const data = res[1].data.result.replay
      game.start(data)
    })
    .catch()
}

if (id) {
  loadAll(id)
}

clickBtn.addEventListener('click', function (e) {
  loadAll(input.value)
})

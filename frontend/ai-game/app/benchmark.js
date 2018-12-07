import config from './config'
import axios from 'axios'
import createItems from './createRankItem' 

axios.get(config.rest['benchmark'])
  .then(res => {
    const data = res.data['data']
    const html = createItems(data, 'benchmark')
    document.querySelector('#rank').innerHTML = html
  })
  .catch(err => {
  })
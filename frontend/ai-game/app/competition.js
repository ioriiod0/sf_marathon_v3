import config from './config'
import axios from 'axios'
import createItems from './createRankItem' 

axios.get(config.rest['competition'])
  .then(res => {
    const data = res.data['data']
    const html = createItems(data, 'competition')
    document.querySelector('#rank').innerHTML = html
  })
  .catch(err => {
  })
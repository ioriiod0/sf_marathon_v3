
function createEnv (envs, type) {
  return envs.reduce((str, env) => {
   return str + `<div class="rank__env-item"><a href="/?id=${env.id}&type=${type}" target="_blank">${env.score}</a></div>`
  }, '')
}

export default function createItems (data, type) {
  return data.reduce((str, item) => {
    const env = createEnv(item.envs, type)
    return str + `<li class="rank__item">
        <div class="rank__detail">
          <div class="rank__name">${item.name}</div>
          <div class="rank__envs">${env}</div>
        </div>
        <div class="rank__avg-score">${item.avg_score}</div>
      </li>`
  }, '')
}

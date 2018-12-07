import * as createjs from 'createjs-module'

const PLAYER_NUM = 2

export default class Game {
  constructor (canvas, size, manifest) {
    this.walls = []
    this.packageContainer = null
    this.images = {}
    // init stage
    this.stage = new createjs.Stage(canvas)
    this.queue = new createjs.LoadQueue()
    this.stageWidth = this.stage.canvas.offsetWidth
    this.podSize = this.stageWidth / size
    this.scale = this.podSize / 120
    this.oldExpressman = []
    this.players = []
    this.score = 0
    this.homes = []
    // create background
    this.createScene(size)
  }
  preLoad (manifest) {
    return this.loadImages(manifest)
    .then(data => {
      data.forEach(item => {
        this.images[item.id] = item.img
      })
      // create expressman
      for(let i = 0; i < PLAYER_NUM; i++) {
        const player = new createjs.Bitmap(this.images['person' + (i+1)])
        player.x = 0
        player.y = 0

        player.scaleX = this.scale
        player.scaleY = this.scale

        this.oldPlayers && this.stage.removeChild(this.oldPlayers)
        this.oldPlayers = []
        this.oldPlayers.push(player)
        
        this.stage.addChild(player)
        this.players.push(player)
      }
    })
  }
  loadImages (manifest) {
    function load (item) {
      return new Promise((resolve, reject) => {
        const img = new Image()
        img.onload = function () {
          resolve({id: item.id, img: img})
        }
        img.onerror = function () {
          alert('图片加载错误，请刷新浏览器！')
        }
        img.src = item.src
      })
    }
    return Promise.all(manifest.map(item => load(item)))
  }
  paint (step, isInit) {
    const { player1, player2, walls, jobs } = step
    const player1_home = [player1.home_x, player1.home_y]
    const player2_home = [player2.home_x, player2.home_y]

    if (isInit) {
      this.players.forEach(player => this.stage.addChild(player))
      // create walls
      for(let i = 0; i < walls.length; i++) {
        this.walls[i] = new createjs.Bitmap(this.images['wall'])
        this.walls[i].scaleX = this.scale
        this.walls[i].scaleY = this.scale
        this.walls[i].y = walls[i].x * this.podSize
        this.walls[i].x = walls[i].y * this.podSize
      }
      this.stage.addChild.apply(this.stage, this.walls)
    }

    const ais = [player1, player2]
    ais.forEach((ai, index) => {
      this.players[index].x = ai.y * this.podSize
      this.players[index].y = ai.x * this.podSize
    })
    // delete old packageContainer
    this.packageContainer && this.stage.removeChild(this.packageContainer)

    // create package
    this.packageContainer = this.createPackage(jobs)
    this.stage.addChild(this.packageContainer)

    this.homes.forEach(home => this.stage.removeChild(home))
    this.homes = this.createHome([player1_home, player2_home])
    this.homes.forEach(home => this.stage.addChild(home))

    // score
    ais.forEach((ai, index) => {
      const event = new CustomEvent('addScore', { 
        detail: { 
          score: ai.score, 
          jobs: ai.n_jobs,
          value: ai.value,
          player: index, 
        }
      })
      window.dispatchEvent(event)
    })
  }

  createScene (size) {
    const containers = []
    for(let i = 0; i < size; i++) {
      for(let j = 0; j < size; j++) {
        const container = new createjs.Container()
        const type = (i + j) % 2 ? 'dark' : 'light'
        const bg = this.createBg(type)
        container.setBounds(
          j * this.podSize,
          i * this.podSize,
          this.podSize,
          this.podSize
        )
        container.x = j * this.podSize
        container.y = i * this.podSize
        container.addChild(bg)
        containers.push(container)
      }
    }
    this.stage.addChild.apply(this.stage, containers)
    this.stage.update()
  }
  createPackage (packages) {
    const container = new createjs.Container()
    packages.forEach(p => {
      const pBitmap = new createjs.Bitmap(this.images['package'])
      const pText = new createjs.Text(p.value, "20px Arial", "#ff7700")
      pBitmap.scaleX = this.scale
      pBitmap.scaleY = this.scale
      pBitmap.y = p.x * this.podSize
      pBitmap.x = p.y * this.podSize
      pText.y = p.x * this.podSize
      pText.x = p.y * this.podSize
      container.addChild(pBitmap, pText)
    })
    container.x = 0
    container.y = 0
    return container
  }
  createBg (type) {
    let graphics
    if (type === 'dark') {
      graphics = new createjs.Graphics().beginFill("#dddddd").drawRect(0, 0, this.podSize, this.podSize)
    } else if (type === 'light') {
      graphics = new createjs.Graphics().beginFill("#ffffff").drawRect(0, 0, this.podSize, this.podSize)
    }
    return new createjs.Shape(graphics)
  }
  createHome(homes) {
    const colors = ['#DC143C', '#0000CD']
    return homes.map((home, index) => {
      const pText = new createjs.Text('货仓', "20px Arial", colors[index])
      pText.y = home[0] * this.podSize
      pText.x = home[1] * this.podSize
      return pText
    })
  }
  start (data) {
    let isInit = true
    const event1 = new CustomEvent('addScore', { detail: {
      score: 0, 
      jobs: 0,
      value: 0,
      player: 0, 
    }})
    const event2 = new CustomEvent('addScore', { detail: {
      score: 0, 
      jobs: 0,
      value: 0,
      player: 1, 
    }})
    window.dispatchEvent(event1)
    window.dispatchEvent(event2)
    createjs.Ticker.framerate = 2
    
    // bind update tick
    createjs.Ticker.addEventListener("tick", () => {
      if (data.length > 0) {
        this.paint(data.shift(), isInit)
        isInit = isInit && !isInit
      } else {
        createjs.Ticker.removeAllEventListeners("tick")
        alert('演示结束！')
      }
      this.stage.update()
    })
  }

  startManual (data) {
    let isInit = true
    createjs.Ticker.framerate = 1

    // bind update tick
    createjs.Ticker.addEventListener("tick", () => {
      if (data.length > 0) {
        this.paint(data.shift(), isInit)
        isInit = isInit && !isInit
      } else {
        createjs.Ticker.removeAllEventListeners("tick")
        alert('演示结束！')
      }
      this.stage.update()
    })
  }
}

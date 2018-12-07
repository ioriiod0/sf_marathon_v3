const path = require('path');
module.exports = {
  entry: {
    app: path.join(__dirname, 'app', 'index'),
    competition: path.join(__dirname, 'app', 'competition'),
    benchmark: path.join(__dirname, 'app', 'benchmark'),
    hand: path.join(__dirname, 'app', 'manual')
  },
  output: {
    filename: 'bundle-[name].js',
    path: path.resolve(__dirname, 'dist')
  },
  module: {
    rules: [{
      test: /.jsx?$/,
      include: [
        path.resolve(__dirname, 'app')
      ],
      exclude: [
        path.resolve(__dirname, 'node_modules'),
        path.resolve(__dirname, 'bower_components')
      ],
      loader: 'babel-loader',
      query: {
        presets: ['es2015']
      }
    }]
  },
  resolve: {
    extensions: ['.json', '.js', '.jsx', '.css']
  },
  devtool: 'source-map',
  devServer: {
    publicPath: path.join('/dist/')
  }
};
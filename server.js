const express = require('express');
const { exec } = require('child_process');

const app = express();
const port = 3000;

// Serve static files from 'public' directory
app.use(express.static('public'));

app.listen(port, () => {
  console.log(`Server running at http://localhost:${port}/`);
});

app.get('/refresh', (req, res) => {
  exec('python collect_stats.py', (error, stdout, stderr) => {
      if (error) {
          console.error(`exec error: ${error}`);
          return res.status(500).send("Error executing the Python script.");
      }
      res.send("Data refreshed successfully.");
  });
});

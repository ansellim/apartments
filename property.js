// Old JS code for downloading the URA property transaction data. This code is legacy code since I have now reimplemented this in Python. Bye Javascript!

require("dotenv").config();
const express = require("express");
const app = express();
const port = 3000;
const axios = require("axios");

var options = {
  headers: { AccessKey: process.env.ACCESSKEY, Token: "" },
};

var updateTimePeriod = 1000 * 60 * 60 * 24;
var data;

const updateToken = () => {
  console.log("Updating token");
  axios
    .get("https://www.ura.gov.sg/uraDataService/insertNewToken.action", options)
    .then(function (response) {
      options.headers.Token = response.data.Result;
      console.log("Access token: " + options.headers.Token);
    })
    .catch((error) => {
      console.log("Error: " + error);
    });
};

// Collect data
const collectData = () => {
  console.log("Collecting data");
  axios
    .get(
      "https://www.ura.gov.sg/uraDataService/invokeUraDS?service=PMI_Resi_Transaction&batch=1",
      options
    )
    .then(function (response) {
      //console.log(response.data);
      data = response.data;
      console.log(data);
    })
    .catch((error) => {
      console.log("Error: " + error);
    });
};

// Express stuff
app.listen(port, () => {
  console.log(`app listening at http://localhost:${port}`);
});

// Update token every day
updateToken();
setInterval(updateToken, updateTimePeriod);
updateLoop();

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function updateLoop() {
  console.log("Let's wait a while for the token to be updated");
  await sleep(120000); // two minutes
  await collectData();
  await sleep(updateTimePeriod);
}

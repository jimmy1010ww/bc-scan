
var dataSource_number_of_scans = {
    chart: {
        caption: "掃描件數",
        lowerlimit: "0",
        upperlimit: "20",
        showvalue: "1",
        numbersuffix: "件",
        theme: "candy",
        showtooltip: "0"
    },
    colorrange: {
        color: [
            {
                minvalue: "0",
                maxvalue: "100",
                code: "#62B58F"
            }
        ]
    },
    dials: {
        dial: [
            {
                value: "81"
            }
        ]
    }
};

var dataSource_number_of_explit = {
    chart: {
        caption: "弱點數量",
        lowerlimit: "0",
        upperlimit: "20",
        showvalue: "1",
        numbersuffix: "件",
        theme: "candy",
        showtooltip: "0"
    },
    colorrange: {
        color: [
            {
                minvalue: "0",
                maxvalue: "5",
                code: "#62B58F"
            },
            {
                minvalue: "6",
                maxvalue: "10",
                code: "#FF9933"
            },
            {
                minvalue: "11",
                maxvalue: "20",
                code: "#FF3333"
            }
        ]
    },
    dials: {
        dial: [
            {
                value: "81"
            }
        ]
    }
};

var dataSource = {
    chart: {
      caption: "Market Share of Web Servers",
      plottooltext: "<b>$percentValue</b> of web servers run on $label servers",
      showlegend: "1",
      showpercentvalues: "1",
      legendposition: "bottom",
      usedataplotcolorforlabels: "1",
      theme: "candy"
    },
    data: [
      {
        label: "Apache",
        value: "32647479"
      },
      {
        label: "Microsoft",
        value: "22100932"
      },
      {
        label: "Zeus",
        value: "14376"
      },
      {
        label: "Other",
        value: "18674221"
      }
    ]
  };

var number_of_scans_chart;
var number_of_exploit_chart;
var myChart

FusionCharts.ready(function () {
    number_of_scans_chart = new FusionCharts({
        type: "angulargauge",
        renderAt: "chart-container-number-of-scans",
        dataFormat: "json",
        dataSource: dataSource_number_of_scans
    }).render();

    number_of_exploit_chart = new FusionCharts({
        type: "angulargauge",
        renderAt: "chart-container-number-of-exploit",
        dataFormat: "json",
        dataSource: dataSource_number_of_explit
    }).render();

    myChart = new FusionCharts({
        type: "pie2d",
        renderAt: "chart-container-number-type-vulnerabilities",
        dataFormat: "json",
        dataSource
      }).render();
});

$(document).ready(function () {
    // get_task_num
    $.ajax({
        url: "/get_task_num", 
        type: "GET",
        dataType: "json",
        success: function (data) {
            update_number_of_scans(data.value);
            console.log("Success getting get_task_num:", data);
        },
        error: function (error) {
            console.log("Error getting get_task_num:", error);
        }
    });

    $.ajax({
        url: "/get_task_num",
        type: "GET",
        dataType: "json",
        success: function (data) {
            update_number_of_exploit(data.value);
            console.log("获取数据成功:", data);
        },
        error: function (error) {
            console.log("获取数据时发生错误:", error);
        }
    });

    
    function update_number_of_scans(value) {
        dataSource_number_of_scans.dials.dial[0].value = value;

        number_of_scans_chart.setJSONData(dataSource_number_of_scans);
    }

    function update_number_of_exploit(value) {
        dataSource_number_of_explit.dials.dial[0].value = value;

        number_of_exploit_chart.setJSONData(dataSource_number_of_explit);
    }
});

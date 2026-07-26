const riskDataElement = document.getElementById('risk-data');
const riskData = riskDataElement ? JSON.parse(riskDataElement.textContent) : {
    critical: 0,
    high: 0,
    medium: 0,
    low: 0
};

const ctx=document.getElementById('riskChart');

new Chart(ctx,{

type:'bar',

data:{

labels:['Critical','High','Medium','Low'],

datasets:[{

label:'Risks',

data:[
    riskData.critical,
    riskData.high,
    riskData.medium,
    riskData.low
],

backgroundColor:[
'#dc2626',
'#ea580c',
'#2563eb',
'#16a34a'
]

}]

},

options:{

responsive:true,

plugins:{

legend:{

display:false

}

}

}

});

const compliance = document.getElementById("complianceChart");

new Chart(compliance, {

    type: "doughnut",

    data: {

        labels: ["Compliant", "Pending"],

        datasets: [{

            data: [
                riskData.compliance,
                100 - riskData.compliance
            ],

            backgroundColor: [
                "#16a34a",
                "#dc2626"
            ]

        }]

    },

    options: {

        responsive: true,

        plugins: {

            legend: {

                position: "bottom"

            }

        }

    }

});
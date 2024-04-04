console.log('in')

function BubbleChart(svg, data) {
    
    // Color palette for continents?
    var color = d3.scaleOrdinal()
        .domain(["Asia", "Europe", "Africa", "Oceania", "Americas"])
        .range(d3.schemeSet1);

    // Size scale for countries
    var size = d3.scaleLinear()
        .domain([1, 15])
        .range([20,40])  // circle will be between 7 and 55 px wide

    var node = svg.append("g")
        .selectAll("circle")
        .data(data)
        .enter()
        .append("circle")
        .attr("class", "node")
        .attr("r", function(d){ return size(d.cnt)})
        .attr("cx", width / 2)
        .attr("cy", height / 2)
        .style("fill", "#69b3a2")  //function(d){ return color(d.region)}
        .style("fill-opacity", 0.8)
        .attr("stroke", "black")
        .style("stroke-width", 3)
        .call(d3.drag() // call specific function when circle is dragged
            .on("start", dragstarted)
            .on("drag", dragged)
            .on("end", dragended));

    let textElems = svg.selectAll(null)
            .data(data)
            .enter()
            .append('text')
            .attr("text-anchor", "middle")
            .text(d => d.kwd)
            .attr('color', 'black')
            .attr('text-shadow', '#FC0 1px 0 10px;')
            .attr('font-size', 12)

    console.log(textElems)
    // Features of the forces applied to the nodes:
    var simulation = d3.forceSimulation()
                        .force("center", d3.forceCenter().x(width / 2).y(height / 2)) // Attraction to the center of the svg area
                        .force("charge", d3.forceManyBody().strength(.1)) // Nodes are attracted one each other of value is > 0
                        .force("collide", d3.forceCollide().strength(.2).radius(function(d){ return (size(d.cnt)+3) }).iterations(1)) // Force that avoids circle overlapping


    simulation
        .nodes(data)
        .on("tick", function(d){
            node
                .attr("cx", function(d){ return d.x; })
                .attr("cy", function(d){ return d.y; })
            textElems.attr('x', (d) => {return d.x})
                .attr('y', (d) => { return d.y});
        });
    
    // What happens when a circle is dragged?
    function dragstarted(d) {
        if (!d3.event.active) simulation.alphaTarget(.03).restart();
        d.fx = d.x;
        d.fy = d.y;
    }
    function dragged(d) {
        d.fx = d3.event.x;
        d.fy = d3.event.y;
    }
    function dragended(d) {
        if (!d3.event.active) simulation.alphaTarget(.03);
        d.fx = null;
        d.fy = null;
    }

}
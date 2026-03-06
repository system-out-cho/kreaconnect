import { app } from "../../../scripts/app.js";
import {api} from "../../../scripts/api.js";

console.log("testing");
console.log(app);

const nodes = new Map([
  ['GPT Image', 184],
  ['Z Image', 3],
]);

app.registerExtension({
    name: "KreaNode.CostBadge",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        const value = nodes.get(nodeData.name);
        if (value != null) {
            // This method runs every time the node is drawn on the screen
            const onDrawForeground = nodeType.prototype.onDrawForeground;
            nodeType.prototype.onDrawForeground = function(ctx) {
                const r = onDrawForeground ? onDrawForeground.apply(this, arguments) : undefined;
                
                // Set the style for your credit flag
                ctx.fillStyle = "#444444"; // Yellow background
                ctx.beginPath();
                ctx.roundRect(this.size[0] - 70, -25, 65, 18, 5); // Position it top-right
                ctx.fill();
                
                ctx.fillStyle = "#ffffff";
                ctx.font = "bold 10px sans-serif";
                ctx.fillText(`⚡${value} CU`, this.size[0] - 60, - 12);
                
                return r;
        }
        }
    }
});
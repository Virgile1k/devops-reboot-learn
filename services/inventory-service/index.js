const express = require('express');

const app = express();
const port = 3001;

app.use(express.json());

app.get('/health', (_req, res) => {
  res.json({
    status: 'ok',
    service: 'inventory-service',
    stack: 'Node.js / Express',
  });
});

app.get('/', (_req, res) => {
  res.json({
    service: 'inventory-service',
    items: [
      { id: 1, sku: 'WIDGET-001', quantity: 42 },
      { id: 2, sku: 'GADGET-002', quantity: 17 },
    ],
  });
});

app.listen(port, () => {
  console.log(`inventory-service listening on port ${port}`);
});

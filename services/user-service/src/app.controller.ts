import { Controller, Get } from '@nestjs/common';

@Controller()
export class AppController {
  @Get('health')
  health() {
    return {
      status: 'ok',
      service: 'user-service',
      stack: 'NestJS',
    };
  }

  @Get()
  listUsers() {
    return {
      service: 'user-service',
      users: [
        { id: 1, name: 'Alice', role: 'admin' },
        { id: 2, name: 'Bob', role: 'user' },
      ],
    };
  }
}
